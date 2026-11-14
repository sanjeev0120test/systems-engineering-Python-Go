// Step 38 — Resilient HTTP client: retry with exponential backoff + full jitter,
// circuit breaker (closed → open → half-open), retryable vs permanent errors.
//
// Java analogy: Resilience4j @Retry + @CircuitBreaker around a WebClient call.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"net/http/httptest"
	"strconv"
	"sync"
	"sync/atomic"
	"time"
)

// ---------------------------------------------------------------------------
// Error classification
// ---------------------------------------------------------------------------

type permanentError struct{ err error }

func (p *permanentError) Error() string { return p.err.Error() }
func (p *permanentError) Unwrap() error { return p.err }

// Permanent marks an error as not worth retrying (bad request, 404, decode error).
func Permanent(err error) error {
	if err == nil {
		return nil
	}
	return &permanentError{err: err}
}

// IsPermanent reports whether err (or anything it wraps) was marked Permanent.
func IsPermanent(err error) bool {
	var p *permanentError
	return errors.As(err, &p)
}

// StatusError is an unexpected HTTP status from the dependency.
type StatusError struct {
	Code       int
	RetryAfter time.Duration
}

func (e *StatusError) Error() string { return fmt.Sprintf("unexpected status %d", e.Code) }

// RetryAfterDelay exposes the server's Retry-After hint to Retry.
func (e *StatusError) RetryAfterDelay() time.Duration { return e.RetryAfter }

type retryAfterHinter interface{ RetryAfterDelay() time.Duration }

// ParseRetryAfter accepts both RFC 9110 forms: delay-seconds or an HTTP-date.
func ParseRetryAfter(v string, now time.Time) time.Duration {
	if v == "" {
		return 0
	}
	if secs, err := strconv.Atoi(v); err == nil {
		if secs < 0 {
			return 0
		}
		return time.Duration(secs) * time.Second
	}
	if at, err := http.ParseTime(v); err == nil {
		if d := at.Sub(now); d > 0 {
			return d
		}
	}
	return 0
}

// ---------------------------------------------------------------------------
// Circuit breaker
// ---------------------------------------------------------------------------

// ErrCircuitOpen is returned without calling the dependency while the breaker is open.
var ErrCircuitOpen = errors.New("circuit breaker is open")

// State of the breaker.
type State int

const (
	StateClosed State = iota
	StateOpen
	StateHalfOpen
)

func (s State) String() string {
	switch s {
	case StateClosed:
		return "closed"
	case StateOpen:
		return "open"
	case StateHalfOpen:
		return "half-open"
	}
	return "unknown"
}

// BreakerConfig tunes the breaker.
type BreakerConfig struct {
	FailureThreshold int           // consecutive failures that trip the breaker
	OpenTimeout      time.Duration // fail-fast period before probing again
	HalfOpenMaxCalls int           // concurrent probes allowed while half-open
	SuccessThreshold int           // probe successes required to close
	Now              func() time.Time
	// OnStateChange runs while the breaker lock is held; it must not call the breaker.
	OnStateChange func(from, to State)
}

// CircuitBreaker stops calling a failing dependency so it can recover.
type CircuitBreaker struct {
	mu        sync.Mutex
	cfg       BreakerConfig
	state     State
	gen       uint64
	failures  int
	successes int
	inFlight  int
	openedAt  time.Time
}

// NewCircuitBreaker fills defaults for zero fields.
func NewCircuitBreaker(cfg BreakerConfig) *CircuitBreaker {
	if cfg.FailureThreshold <= 0 {
		cfg.FailureThreshold = 5
	}
	if cfg.OpenTimeout <= 0 {
		cfg.OpenTimeout = 30 * time.Second
	}
	if cfg.HalfOpenMaxCalls <= 0 {
		cfg.HalfOpenMaxCalls = 1
	}
	if cfg.SuccessThreshold <= 0 {
		cfg.SuccessThreshold = 1
	}
	if cfg.Now == nil {
		cfg.Now = time.Now
	}
	return &CircuitBreaker{cfg: cfg}
}

// State returns the current state (transitions to half-open lazily on next call).
func (cb *CircuitBreaker) State() State {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	return cb.state
}

// Execute runs fn if allowed and records the outcome. Permanent errors are the
// caller's fault and do not count against the dependency's health.
func (cb *CircuitBreaker) Execute(fn func() error) error {
	gen, err := cb.admit()
	if err != nil {
		return err
	}
	err = fn()
	cb.record(gen, err != nil && !IsPermanent(err))
	return err
}

func (cb *CircuitBreaker) admit() (uint64, error) {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	switch cb.state {
	case StateOpen:
		if cb.cfg.Now().Sub(cb.openedAt) < cb.cfg.OpenTimeout {
			return 0, ErrCircuitOpen
		}
		cb.setState(StateHalfOpen)
		fallthrough
	case StateHalfOpen:
		if cb.inFlight >= cb.cfg.HalfOpenMaxCalls {
			return 0, ErrCircuitOpen
		}
		cb.inFlight++
	}
	return cb.gen, nil
}

func (cb *CircuitBreaker) record(gen uint64, failed bool) {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	if gen != cb.gen {
		return
	}
	switch cb.state {
	case StateClosed:
		if !failed {
			cb.failures = 0
			return
		}
		cb.failures++
		if cb.failures >= cb.cfg.FailureThreshold {
			cb.trip()
		}
	case StateHalfOpen:
		cb.inFlight--
		if failed {
			cb.trip()
			return
		}
		cb.successes++
		if cb.successes >= cb.cfg.SuccessThreshold {
			cb.setState(StateClosed)
		}
	}
}

func (cb *CircuitBreaker) trip() {
	cb.setState(StateOpen)
	cb.openedAt = cb.cfg.Now()
}

func (cb *CircuitBreaker) setState(to State) {
	if cb.state == to {
		return
	}
	from := cb.state
	cb.state = to
	cb.gen++
	cb.failures, cb.successes, cb.inFlight = 0, 0, 0
	if cb.cfg.OnStateChange != nil {
		cb.cfg.OnStateChange(from, to)
	}
}

// ---------------------------------------------------------------------------
// Retry with backoff
// ---------------------------------------------------------------------------

// RetryPolicy is exponential backoff with full jitter (AWS Architecture Blog).
type RetryPolicy struct {
	MaxAttempts int
	BaseDelay   time.Duration
	MaxDelay    time.Duration
	Rand        func() float64
	Sleep       func(ctx context.Context, d time.Duration) error
}

func sleepCtx(ctx context.Context, d time.Duration) error {
	t := time.NewTimer(d)
	defer t.Stop()
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-t.C:
		return nil
	}
}

// Backoff returns a random delay in [0, min(MaxDelay, BaseDelay*2^attempt)).
// Full jitter spreads retries so recovering services are not hit in lockstep.
func (p RetryPolicy) Backoff(attempt int) time.Duration {
	ceiling := p.MaxDelay
	if attempt < 32 {
		if c := p.BaseDelay << attempt; c > 0 && c < p.MaxDelay {
			ceiling = c
		}
	}
	r := p.Rand
	if r == nil {
		r = rand.Float64
	}
	return time.Duration(r() * float64(ceiling))
}

// Retry calls fn until success, a permanent error, an open circuit, ctx done,
// or MaxAttempts. It returns the number of attempts made.
func Retry(ctx context.Context, p RetryPolicy, fn func(ctx context.Context) error) (int, error) {
	if p.MaxAttempts <= 0 {
		p.MaxAttempts = 1
	}
	sleep := p.Sleep
	if sleep == nil {
		sleep = sleepCtx
	}
	var err error
	for attempt := 0; attempt < p.MaxAttempts; attempt++ {
		if cerr := ctx.Err(); cerr != nil {
			return attempt, cerr
		}
		err = fn(ctx)
		if err == nil || IsPermanent(err) || errors.Is(err, ErrCircuitOpen) {
			return attempt + 1, err
		}
		if attempt == p.MaxAttempts-1 {
			break
		}
		delay := p.Backoff(attempt)
		var hint retryAfterHinter
		if errors.As(err, &hint) && hint.RetryAfterDelay() > delay {
			delay = hint.RetryAfterDelay()
			if p.MaxDelay > 0 && delay > p.MaxDelay {
				delay = p.MaxDelay
			}
		}
		if serr := sleep(ctx, delay); serr != nil {
			return attempt + 1, serr
		}
	}
	return p.MaxAttempts, fmt.Errorf("gave up after %d attempts: %w", p.MaxAttempts, err)
}

// ---------------------------------------------------------------------------
// Client = timeout + retry + breaker
// ---------------------------------------------------------------------------

// Client wraps http.Client with per-attempt timeouts, retries, and a breaker.
type Client struct {
	HTTP           *http.Client
	Breaker        *CircuitBreaker
	Policy         RetryPolicy
	AttemptTimeout time.Duration
}

// GetJSON fetches url and decodes the JSON body into out.
func (c *Client) GetJSON(ctx context.Context, url string, out any) (int, error) {
	return Retry(ctx, c.Policy, func(ctx context.Context) error {
		return c.Breaker.Execute(func() error { return c.once(ctx, url, out) })
	})
}

func (c *Client) once(ctx context.Context, url string, out any) error {
	if c.AttemptTimeout > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, c.AttemptTimeout)
		defer cancel()
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return Permanent(err)
	}
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	switch {
	case resp.StatusCode == http.StatusTooManyRequests || resp.StatusCode >= 500:
		_, _ = io.Copy(io.Discard, resp.Body)
		return &StatusError{Code: resp.StatusCode, RetryAfter: ParseRetryAfter(resp.Header.Get("Retry-After"), time.Now())}
	case resp.StatusCode >= 400:
		_, _ = io.Copy(io.Discard, resp.Body)
		return Permanent(&StatusError{Code: resp.StatusCode})
	}
	if err := json.NewDecoder(resp.Body).Decode(out); err != nil {
		return Permanent(fmt.Errorf("decode response: %w", err))
	}
	return nil
}

func main() {
	fmt.Println("Step 38 — Resilient client demo (retry + jitter + circuit breaker)")

	var flakyHits atomic.Int64
	flaky := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if flakyHits.Add(1) <= 2 {
			http.Error(w, "upstream overloaded", http.StatusServiceUnavailable)
			return
		}
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok", "region": "eu-west-1"})
	}))
	defer flaky.Close()

	var deadHits atomic.Int64
	dead := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		deadHits.Add(1)
		http.Error(w, "db connection pool exhausted", http.StatusInternalServerError)
	}))
	defer dead.Close()

	newClient := func(name string) *Client {
		return &Client{
			HTTP: &http.Client{},
			Breaker: NewCircuitBreaker(BreakerConfig{
				FailureThreshold: 3,
				OpenTimeout:      200 * time.Millisecond,
				OnStateChange: func(from, to State) {
					fmt.Printf("    [breaker %s] %s -> %s\n", name, from, to)
				},
			}),
			Policy:         RetryPolicy{MaxAttempts: 4, BaseDelay: 10 * time.Millisecond, MaxDelay: 100 * time.Millisecond},
			AttemptTimeout: time.Second,
		}
	}

	ctx := context.Background()

	fmt.Println("\n[1] Transient 503s: retry with jittered backoff until success")
	var body map[string]string
	c := newClient("payments")
	attempts, err := c.GetJSON(ctx, flaky.URL, &body)
	fmt.Printf("    attempts=%d err=%v body=%v\n", attempts, err, body)

	fmt.Println("\n[2] Hard-down dependency: breaker trips, later calls fail fast")
	d := newClient("inventory")
	for i := 1; i <= 3; i++ {
		attempts, err := d.GetJSON(ctx, dead.URL, &body)
		fmt.Printf("    call %d: attempts=%d err=%v server_hits=%d\n", i, attempts, err, deadHits.Load())
	}

	fmt.Println("\n[3] After OpenTimeout the breaker half-opens and sends one probe (still down -> re-opens)")
	time.Sleep(250 * time.Millisecond)
	attempts, err = d.GetJSON(ctx, dead.URL, &body)
	fmt.Printf("    probe: attempts=%d err=%v state=%s server_hits=%d\n", attempts, err, d.Breaker.State(), deadHits.Load())

	fmt.Println("\n[4] 404 is permanent: no retries, breaker unaffected")
	notFound := httptest.NewServer(http.NotFoundHandler())
	defer notFound.Close()
	n := newClient("catalog")
	attempts, err = n.GetJSON(ctx, notFound.URL, &body)
	fmt.Printf("    attempts=%d permanent=%v err=%v state=%s\n", attempts, IsPermanent(err), err, n.Breaker.State())
}
