// Step 37 — Production API gateway: middleware chain, per-client rate limiting,
// request IDs, panic recovery, timeouts, body limits, graceful shutdown.
//
// Java analogy: Spring Cloud Gateway filters + Bucket4j + Resilience4j TimeLimiter.
package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"math"
	"net"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"
)

// ---------------------------------------------------------------------------
// Token bucket rate limiting
// ---------------------------------------------------------------------------

// TokenBucket allows bursts up to capacity and refills at rate tokens/second.
type TokenBucket struct {
	mu       sync.Mutex
	capacity float64
	tokens   float64
	rate     float64
	last     time.Time
}

// NewTokenBucket returns a full bucket.
func NewTokenBucket(capacity int, ratePerSec float64, now time.Time) *TokenBucket {
	return &TokenBucket{capacity: float64(capacity), tokens: float64(capacity), rate: ratePerSec, last: now}
}

// Allow consumes one token; when empty it reports how long until one is available.
func (b *TokenBucket) Allow(now time.Time) (bool, time.Duration) {
	b.mu.Lock()
	defer b.mu.Unlock()
	if elapsed := now.Sub(b.last).Seconds(); elapsed > 0 {
		b.tokens = math.Min(b.capacity, b.tokens+elapsed*b.rate)
		b.last = now
	}
	if b.tokens >= 1 {
		b.tokens--
		return true, 0
	}
	wait := time.Duration((1 - b.tokens) / b.rate * float64(time.Second))
	return false, wait
}

type clientBucket struct {
	bucket   *TokenBucket
	lastSeen time.Time
}

// ClientLimiter keeps one bucket per client (API key or IP).
type ClientLimiter struct {
	mu       sync.Mutex
	buckets  map[string]*clientBucket
	capacity int
	rate     float64
	idleTTL  time.Duration
	now      func() time.Time
}

// NewClientLimiter builds a per-client limiter. now is injectable for tests.
func NewClientLimiter(capacity int, ratePerSec float64, idleTTL time.Duration, now func() time.Time) *ClientLimiter {
	if now == nil {
		now = time.Now
	}
	return &ClientLimiter{
		buckets:  make(map[string]*clientBucket),
		capacity: capacity,
		rate:     ratePerSec,
		idleTTL:  idleTTL,
		now:      now,
	}
}

// Allow checks the bucket for one client.
func (l *ClientLimiter) Allow(client string) (bool, time.Duration) {
	now := l.now()
	l.mu.Lock()
	cb, ok := l.buckets[client]
	if !ok {
		cb = &clientBucket{bucket: NewTokenBucket(l.capacity, l.rate, now)}
		l.buckets[client] = cb
	}
	cb.lastSeen = now
	l.mu.Unlock()
	return cb.bucket.Allow(now)
}

// Evict drops idle clients so memory stays bounded when IPs churn (NAT, scanners).
func (l *ClientLimiter) Evict() int {
	cutoff := l.now().Add(-l.idleTTL)
	l.mu.Lock()
	defer l.mu.Unlock()
	removed := 0
	for key, cb := range l.buckets {
		if cb.lastSeen.Before(cutoff) {
			delete(l.buckets, key)
			removed++
		}
	}
	return removed
}

// Len reports how many clients are tracked.
func (l *ClientLimiter) Len() int {
	l.mu.Lock()
	defer l.mu.Unlock()
	return len(l.buckets)
}

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------

// Middleware wraps a handler (like a servlet Filter).
type Middleware func(http.Handler) http.Handler

// Chain applies middleware so the first one listed is the outermost.
func Chain(h http.Handler, mws ...Middleware) http.Handler {
	for i := len(mws) - 1; i >= 0; i-- {
		h = mws[i](h)
	}
	return h
}

type ctxKey string

const requestIDKey ctxKey = "request_id"

// RequestIDFrom returns the correlation ID stored by RequestID.
func RequestIDFrom(ctx context.Context) string {
	id, _ := ctx.Value(requestIDKey).(string)
	return id
}

func newID() string {
	b := make([]byte, 8)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}

// RequestID propagates X-Request-ID from upstream or mints a new one.
func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := r.Header.Get("X-Request-ID")
		if id == "" || len(id) > 64 {
			id = newID()
		}
		w.Header().Set("X-Request-ID", id)
		next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), requestIDKey, id)))
	})
}

type statusRecorder struct {
	http.ResponseWriter
	status int
	bytes  int
}

func (s *statusRecorder) WriteHeader(code int) {
	if s.status == 0 {
		s.status = code
	}
	s.ResponseWriter.WriteHeader(code)
}

func (s *statusRecorder) Write(b []byte) (int, error) {
	if s.status == 0 {
		s.status = http.StatusOK
	}
	n, err := s.ResponseWriter.Write(b)
	s.bytes += n
	return n, err
}

// AccessLog emits one structured JSON line per request.
func AccessLog(logger *slog.Logger) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			rec := &statusRecorder{ResponseWriter: w}
			next.ServeHTTP(rec, r)
			if rec.status == 0 {
				rec.status = http.StatusOK
			}
			logger.Info("request",
				"request_id", RequestIDFrom(r.Context()),
				"method", r.Method,
				"path", r.URL.Path,
				"status", rec.status,
				"bytes", rec.bytes,
				"duration_ms", time.Since(start).Milliseconds(),
				"client", ClientKey(r),
			)
		})
	}
}

// Recover turns a handler panic into a 500 instead of killing the connection.
func Recover(logger *slog.Logger) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer func() {
				if v := recover(); v != nil {
					if v == http.ErrAbortHandler {
						panic(v)
					}
					logger.Error("panic recovered", "request_id", RequestIDFrom(r.Context()), "panic", fmt.Sprint(v))
					writeJSON(w, http.StatusInternalServerError, map[string]string{
						"error":      "internal server error",
						"request_id": RequestIDFrom(r.Context()),
					})
				}
			}()
			next.ServeHTTP(w, r)
		})
	}
}

// ClientKey identifies the caller: API key first, then remote IP.
func ClientKey(r *http.Request) string {
	if key := r.Header.Get("X-API-Key"); key != "" {
		return "key:" + key
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		host = r.RemoteAddr
	}
	return "ip:" + host
}

// RateLimit rejects callers over their budget with 429 + Retry-After.
func RateLimit(l *ClientLimiter) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			ok, wait := l.Allow(ClientKey(r))
			if !ok {
				secs := int(math.Ceil(wait.Seconds()))
				if secs < 1 {
					secs = 1
				}
				w.Header().Set("Retry-After", strconv.Itoa(secs))
				writeJSON(w, http.StatusTooManyRequests, map[string]string{"error": "rate limit exceeded"})
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

// ---------------------------------------------------------------------------
// Gateway
// ---------------------------------------------------------------------------

// Config controls gateway limits.
type Config struct {
	RateCapacity   int
	RatePerSec     float64
	RequestTimeout time.Duration
	MaxBodyBytes   int64
	SlowDelay      time.Duration
	Now            func() time.Time
}

// DefaultConfig is a sane production-ish baseline.
func DefaultConfig() Config {
	return Config{
		RateCapacity:   10,
		RatePerSec:     5,
		RequestTimeout: 2 * time.Second,
		MaxBodyBytes:   1 << 20,
		SlowDelay:      3 * time.Second,
	}
}

// Order is the demo API resource.
type Order struct {
	ID          string `json:"id"`
	Customer    string `json:"customer"`
	AmountCents int64  `json:"amount_cents"`
}

func writeJSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(body)
}

func errBody(msg string) map[string]string { return map[string]string{"error": msg} }

// NewGateway wires routes and middleware. /healthz bypasses rate limiting so
// load balancer probes never get throttled.
func NewGateway(cfg Config, logger *slog.Logger) (http.Handler, *ClientLimiter) {
	limiter := NewClientLimiter(cfg.RateCapacity, cfg.RatePerSec, 10*time.Minute, cfg.Now)

	api := http.NewServeMux()
	api.HandleFunc("GET /api/orders/{id}", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, Order{ID: r.PathValue("id"), Customer: "acme-corp", AmountCents: 4999})
	})
	api.HandleFunc("POST /api/orders", func(w http.ResponseWriter, r *http.Request) {
		r.Body = http.MaxBytesReader(w, r.Body, cfg.MaxBodyBytes)
		var o Order
		dec := json.NewDecoder(r.Body)
		dec.DisallowUnknownFields()
		if err := dec.Decode(&o); err != nil {
			var tooBig *http.MaxBytesError
			if errors.As(err, &tooBig) {
				writeJSON(w, http.StatusRequestEntityTooLarge, errBody("request body too large"))
				return
			}
			writeJSON(w, http.StatusBadRequest, errBody("invalid JSON: "+err.Error()))
			return
		}
		if strings.TrimSpace(o.Customer) == "" || o.AmountCents <= 0 {
			writeJSON(w, http.StatusUnprocessableEntity, errBody("customer and positive amount_cents are required"))
			return
		}
		o.ID = "ord_" + newID()
		writeJSON(w, http.StatusCreated, o)
	})
	api.HandleFunc("GET /api/slow", func(w http.ResponseWriter, r *http.Request) {
		select {
		case <-time.After(cfg.SlowDelay):
			writeJSON(w, http.StatusOK, map[string]string{"status": "done"})
		case <-r.Context().Done():
		}
	})
	api.HandleFunc("GET /debug/panic", func(w http.ResponseWriter, r *http.Request) {
		var m map[string]int
		m["boom"] = 1 // nil map write — simulated production bug
	})

	limited := Chain(
		http.TimeoutHandler(api, cfg.RequestTimeout, `{"error":"request timed out"}`),
		RateLimit(limiter),
	)

	root := http.NewServeMux()
	root.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})
	root.Handle("/", limited)

	return Chain(root, RequestID, AccessLog(logger), Recover(logger)), limiter
}

// NewServer applies the timeouts every internet-facing Go server needs
// (the zero-value http.Server has none and is vulnerable to Slowloris).
func NewServer(addr string, h http.Handler) *http.Server {
	return &http.Server{
		Addr:              addr,
		Handler:           h,
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      15 * time.Second,
		IdleTimeout:       60 * time.Second,
		MaxHeaderBytes:    1 << 16,
	}
}

func runDemo() error {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	cfg := DefaultConfig()
	cfg.RateCapacity = 5
	cfg.RatePerSec = 1
	cfg.RequestTimeout = 300 * time.Millisecond
	cfg.SlowDelay = time.Second
	handler, _ := NewGateway(cfg, logger)

	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		return err
	}
	srv := NewServer(ln.Addr().String(), handler)
	go func() { _ = srv.Serve(ln) }()
	base := "http://" + ln.Addr().String()
	client := &http.Client{Timeout: 2 * time.Second}

	call := func(method, path, body, apiKey string) {
		req, _ := http.NewRequest(method, base+path, strings.NewReader(body))
		if apiKey != "" {
			req.Header.Set("X-API-Key", apiKey)
		}
		resp, err := client.Do(req)
		if err != nil {
			fmt.Printf("  %-6s %-22s -> error %v\n", method, path, err)
			return
		}
		b, _ := io.ReadAll(resp.Body)
		resp.Body.Close()
		extra := ""
		if ra := resp.Header.Get("Retry-After"); ra != "" {
			extra = " Retry-After=" + ra
		}
		fmt.Printf("  %-6s %-22s -> %d%s %s\n", method, path, resp.StatusCode, extra, strings.TrimSpace(string(b)))
	}

	fmt.Println("Step 37 — API gateway demo")
	fmt.Println("\n[1] Burst of 7 requests from tenant-a (capacity 5): last two throttled")
	for range 7 {
		call("GET", "/api/orders/42", "", "tenant-a")
	}
	fmt.Println("\n[2] tenant-b has its own bucket — not affected by tenant-a")
	call("GET", "/api/orders/7", "", "tenant-b")
	fmt.Println("\n[3] Health checks bypass the limiter")
	call("GET", "/healthz", "", "tenant-a")
	fmt.Println("\n[4] Validation, unknown fields, and a valid create")
	call("POST", "/api/orders", `{"customer":"","amount_cents":0}`, "tenant-c")
	call("POST", "/api/orders", `{"customer":"x","amount_cents":1,"admin":true}`, "tenant-c")
	call("POST", "/api/orders", `{"customer":"globex","amount_cents":1250}`, "tenant-c")
	fmt.Println("\n[5] Slow upstream cut off by the request timeout")
	call("GET", "/api/slow", "", "tenant-d")
	fmt.Println("\n[6] Handler panic becomes a 500 with request_id, server keeps serving")
	call("GET", "/debug/panic", "", "tenant-d")
	call("GET", "/healthz", "", "")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		return err
	}
	fmt.Println("\nGraceful shutdown complete.")
	return nil
}

func serve(addr string) error {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	handler, limiter := NewGateway(DefaultConfig(), logger)
	srv := NewServer(addr, handler)

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	go func() {
		ticker := time.NewTicker(time.Minute)
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				limiter.Evict()
			}
		}
	}()

	errCh := make(chan error, 1)
	go func() {
		logger.Info("gateway listening", "addr", addr)
		errCh <- srv.ListenAndServe()
	}()

	select {
	case err := <-errCh:
		return err
	case <-ctx.Done():
	}
	logger.Info("shutdown signal received, draining in-flight requests")
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	return srv.Shutdown(shutdownCtx)
}

func main() {
	var err error
	if len(os.Args) > 1 && os.Args[1] == "serve" {
		err = serve("127.0.0.1:8090")
	} else {
		err = runDemo()
	}
	if err != nil && !errors.Is(err, http.ErrServerClosed) {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}
