package main

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

type fakeClock struct {
	mu sync.Mutex
	t  time.Time
}

func (c *fakeClock) Now() time.Time {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.t
}

func (c *fakeClock) Advance(d time.Duration) {
	c.mu.Lock()
	c.t = c.t.Add(d)
	c.mu.Unlock()
}

var errBoom = errors.New("boom")

func fail() error    { return errBoom }
func succeed() error { return nil }

func noSleep(ctx context.Context, _ time.Duration) error { return ctx.Err() }

func TestBreakerFullLifecycle(t *testing.T) {
	clock := &fakeClock{t: time.Unix(0, 0)}
	var transitions []string
	cb := NewCircuitBreaker(BreakerConfig{
		FailureThreshold: 3,
		OpenTimeout:      10 * time.Second,
		SuccessThreshold: 2,
		HalfOpenMaxCalls: 2,
		Now:              clock.Now,
		OnStateChange:    func(from, to State) { transitions = append(transitions, from.String()+">"+to.String()) },
	})

	_ = cb.Execute(fail)
	_ = cb.Execute(fail)
	_ = cb.Execute(succeed) // success resets the consecutive counter
	_ = cb.Execute(fail)
	_ = cb.Execute(fail)
	if cb.State() != StateClosed {
		t.Fatal("breaker should still be closed: failures were not consecutive")
	}
	_ = cb.Execute(fail)
	if cb.State() != StateOpen {
		t.Fatalf("state = %s, want open", cb.State())
	}

	called := false
	if err := cb.Execute(func() error { called = true; return nil }); !errors.Is(err, ErrCircuitOpen) || called {
		t.Fatalf("open breaker must fail fast without calling fn (err=%v called=%v)", err, called)
	}

	clock.Advance(10 * time.Second)
	if err := cb.Execute(succeed); err != nil {
		t.Fatalf("first half-open probe: %v", err)
	}
	if cb.State() != StateHalfOpen {
		t.Fatalf("state = %s, want half-open after 1 of 2 successes", cb.State())
	}
	_ = cb.Execute(succeed)
	if cb.State() != StateClosed {
		t.Fatalf("state = %s, want closed", cb.State())
	}

	want := []string{"closed>open", "open>half-open", "half-open>closed"}
	if len(transitions) != len(want) {
		t.Fatalf("transitions = %v, want %v", transitions, want)
	}
	for i := range want {
		if transitions[i] != want[i] {
			t.Fatalf("transitions = %v, want %v", transitions, want)
		}
	}
}

func TestBreakerHalfOpenFailureReopens(t *testing.T) {
	clock := &fakeClock{t: time.Unix(0, 0)}
	cb := NewCircuitBreaker(BreakerConfig{FailureThreshold: 1, OpenTimeout: time.Second, Now: clock.Now})
	_ = cb.Execute(fail)
	clock.Advance(time.Second)
	_ = cb.Execute(fail)
	if cb.State() != StateOpen {
		t.Fatalf("state = %s, want open after failed probe", cb.State())
	}
	if err := cb.Execute(succeed); !errors.Is(err, ErrCircuitOpen) {
		t.Fatal("re-opened breaker must restart its open timeout")
	}
}

func TestBreakerHalfOpenLimitsConcurrentProbes(t *testing.T) {
	clock := &fakeClock{t: time.Unix(0, 0)}
	cb := NewCircuitBreaker(BreakerConfig{FailureThreshold: 1, OpenTimeout: time.Second, HalfOpenMaxCalls: 1, Now: clock.Now})
	_ = cb.Execute(fail)
	clock.Advance(time.Second)

	release := make(chan struct{})
	started := make(chan struct{})
	done := make(chan error)
	go func() {
		done <- cb.Execute(func() error { close(started); <-release; return nil })
	}()
	<-started
	if err := cb.Execute(succeed); !errors.Is(err, ErrCircuitOpen) {
		t.Fatalf("second concurrent probe err = %v, want ErrCircuitOpen", err)
	}
	close(release)
	if err := <-done; err != nil {
		t.Fatal(err)
	}
	if cb.State() != StateClosed {
		t.Fatalf("state = %s, want closed", cb.State())
	}
}

func TestPermanentErrorsDoNotTrip(t *testing.T) {
	cb := NewCircuitBreaker(BreakerConfig{FailureThreshold: 2})
	for range 10 {
		_ = cb.Execute(func() error { return Permanent(errBoom) })
	}
	if cb.State() != StateClosed {
		t.Fatal("client errors (4xx) must not open the breaker")
	}
}

func TestBackoffFullJitterBounds(t *testing.T) {
	p := RetryPolicy{BaseDelay: 100 * time.Millisecond, MaxDelay: time.Second, Rand: func() float64 { return 0.999999 }}
	wantCeil := []time.Duration{100, 200, 400, 800, 1000, 1000}
	for attempt, ceil := range wantCeil {
		got := p.Backoff(attempt)
		if got > ceil*time.Millisecond || got < (ceil*time.Millisecond)*99/100 {
			t.Fatalf("attempt %d: backoff %v, want just under %vms", attempt, got, ceil)
		}
	}
	if got := p.Backoff(200); got > time.Second {
		t.Fatalf("huge attempt must not overflow: %v", got)
	}
	p.Rand = func() float64 { return 0 }
	if p.Backoff(3) != 0 {
		t.Fatal("full jitter lower bound is 0")
	}
}

func TestRetrySucceedsAfterTransientFailures(t *testing.T) {
	calls := 0
	attempts, err := Retry(context.Background(), RetryPolicy{MaxAttempts: 5, Sleep: noSleep}, func(context.Context) error {
		calls++
		if calls < 3 {
			return errBoom
		}
		return nil
	})
	if err != nil || attempts != 3 {
		t.Fatalf("attempts=%d err=%v, want 3 nil", attempts, err)
	}
}

func TestRetryStopsOnPermanentAndOpenCircuit(t *testing.T) {
	for _, stopErr := range []error{Permanent(errBoom), ErrCircuitOpen} {
		attempts, err := Retry(context.Background(), RetryPolicy{MaxAttempts: 5, Sleep: noSleep}, func(context.Context) error { return stopErr })
		if attempts != 1 || !errors.Is(err, stopErr) {
			t.Fatalf("%v: attempts=%d err=%v, want 1 attempt", stopErr, attempts, err)
		}
	}
}

func TestRetryExhaustionWrapsLastError(t *testing.T) {
	attempts, err := Retry(context.Background(), RetryPolicy{MaxAttempts: 3, Sleep: noSleep}, func(context.Context) error { return errBoom })
	if attempts != 3 || !errors.Is(err, errBoom) {
		t.Fatalf("attempts=%d err=%v", attempts, err)
	}
}

func TestRetryHonorsContextCancellation(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	calls := 0
	_, err := Retry(ctx, RetryPolicy{MaxAttempts: 10, BaseDelay: time.Hour, MaxDelay: time.Hour}, func(context.Context) error {
		calls++
		cancel()
		return errBoom
	})
	if !errors.Is(err, context.Canceled) || calls != 1 {
		t.Fatalf("calls=%d err=%v, want 1 call and context.Canceled", calls, err)
	}
}

func newTestClient() *Client {
	return &Client{
		HTTP:           &http.Client{},
		Breaker:        NewCircuitBreaker(BreakerConfig{FailureThreshold: 3, OpenTimeout: time.Hour}),
		Policy:         RetryPolicy{MaxAttempts: 4, Sleep: noSleep},
		AttemptTimeout: 200 * time.Millisecond,
	}
}

func TestClientRecoversFromTransient503(t *testing.T) {
	var hits atomic.Int64
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if hits.Add(1) <= 2 {
			w.WriteHeader(http.StatusServiceUnavailable)
			return
		}
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	}))
	defer srv.Close()

	var out map[string]string
	attempts, err := newTestClient().GetJSON(context.Background(), srv.URL, &out)
	if err != nil || attempts != 3 || out["status"] != "ok" {
		t.Fatalf("attempts=%d err=%v out=%v", attempts, err, out)
	}
}

func TestClientDoesNotRetry404(t *testing.T) {
	var hits atomic.Int64
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hits.Add(1)
		http.NotFound(w, r)
	}))
	defer srv.Close()

	var out map[string]string
	_, err := newTestClient().GetJSON(context.Background(), srv.URL, &out)
	var se *StatusError
	if !IsPermanent(err) || !errors.As(err, &se) || se.Code != 404 || hits.Load() != 1 {
		t.Fatalf("err=%v hits=%d, want single permanent 404", err, hits.Load())
	}
}

func TestClientBreakerShieldsDeadDependency(t *testing.T) {
	var hits atomic.Int64
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hits.Add(1)
		w.WriteHeader(http.StatusInternalServerError)
	}))
	defer srv.Close()

	c := newTestClient()
	var out map[string]string
	for range 5 {
		_, _ = c.GetJSON(context.Background(), srv.URL, &out)
	}
	if hits.Load() != 3 {
		t.Fatalf("server hits = %d, want 3 (breaker opens after threshold, then fails fast)", hits.Load())
	}
	if c.Breaker.State() != StateOpen {
		t.Fatalf("state = %s, want open", c.Breaker.State())
	}
}

func TestParseRetryAfter(t *testing.T) {
	now := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	cases := map[string]time.Duration{
		"":                              0,
		"7":                             7 * time.Second,
		"-3":                            0,
		"soon":                          0,
		"Thu, 01 Jan 2026 00:00:30 GMT": 30 * time.Second,
		"Wed, 31 Dec 2025 23:59:00 GMT": 0,
	}
	for in, want := range cases {
		if got := ParseRetryAfter(in, now); got != want {
			t.Fatalf("ParseRetryAfter(%q) = %v, want %v", in, got, want)
		}
	}
}

func TestRetryHonorsServerRetryAfterCappedAtMaxDelay(t *testing.T) {
	var hits atomic.Int64
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch hits.Add(1) {
		case 1:
			w.Header().Set("Retry-After", "2")
			w.WriteHeader(http.StatusTooManyRequests)
		case 2:
			w.Header().Set("Retry-After", "3600")
			w.WriteHeader(http.StatusServiceUnavailable)
		default:
			_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
		}
	}))
	defer srv.Close()

	var slept []time.Duration
	c := newTestClient()
	c.Policy = RetryPolicy{
		MaxAttempts: 4,
		BaseDelay:   10 * time.Millisecond,
		MaxDelay:    5 * time.Second,
		Sleep:       func(_ context.Context, d time.Duration) error { slept = append(slept, d); return nil },
	}
	var out map[string]string
	if _, err := c.GetJSON(context.Background(), srv.URL, &out); err != nil {
		t.Fatal(err)
	}
	if len(slept) != 2 || slept[0] != 2*time.Second || slept[1] != 5*time.Second {
		t.Fatalf("slept = %v, want [2s 5s] (server hint, then capped at MaxDelay)", slept)
	}
}

func TestClientPerAttemptTimeoutIsRetried(t *testing.T) {
	var hits atomic.Int64
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if hits.Add(1) == 1 {
			select {
			case <-r.Context().Done():
			case <-time.After(2 * time.Second):
			}
			return
		}
		_ = json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	}))
	defer srv.Close()

	var out map[string]string
	attempts, err := newTestClient().GetJSON(context.Background(), srv.URL, &out)
	if err != nil || attempts != 2 {
		t.Fatalf("attempts=%d err=%v, want hung first attempt timed out then success", attempts, err)
	}
}
