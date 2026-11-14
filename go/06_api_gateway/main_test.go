package main

import (
	"encoding/json"
	"io"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
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

func newTestGateway(t *testing.T, mutate func(*Config)) (http.Handler, *ClientLimiter, *fakeClock) {
	t.Helper()
	clock := &fakeClock{t: time.Unix(1_700_000_000, 0)}
	cfg := DefaultConfig()
	cfg.Now = clock.Now
	cfg.RequestTimeout = 100 * time.Millisecond
	cfg.SlowDelay = 2 * time.Second
	if mutate != nil {
		mutate(&cfg)
	}
	h, l := NewGateway(cfg, slog.New(slog.NewTextHandler(io.Discard, nil)))
	return h, l, clock
}

func do(h http.Handler, method, path, body string, headers map[string]string) *httptest.ResponseRecorder {
	req := httptest.NewRequest(method, path, strings.NewReader(body))
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, req)
	return rec
}

func TestTokenBucketBurstAndRefill(t *testing.T) {
	now := time.Unix(0, 0)
	b := NewTokenBucket(2, 1, now)
	for i := range 2 {
		if ok, _ := b.Allow(now); !ok {
			t.Fatalf("request %d should be allowed within burst", i)
		}
	}
	ok, wait := b.Allow(now)
	if ok {
		t.Fatal("third request should be throttled")
	}
	if wait != time.Second {
		t.Fatalf("wait = %v, want 1s", wait)
	}
	if ok, _ := b.Allow(now.Add(time.Second)); !ok {
		t.Fatal("token should refill after 1s")
	}
	if ok, _ := b.Allow(now.Add(100 * time.Second)); !ok {
		t.Fatal("refill should be allowed after long idle")
	}
	if ok, _ := b.Allow(now.Add(100 * time.Second)); !ok {
		t.Fatal("bucket should hold capacity=2 after long idle")
	}
	if ok, _ := b.Allow(now.Add(100 * time.Second)); ok {
		t.Fatal("bucket must cap at capacity, not accumulate unbounded tokens")
	}
}

func TestRateLimitPerClientWithRetryAfter(t *testing.T) {
	h, _, clock := newTestGateway(t, func(c *Config) { c.RateCapacity = 3; c.RatePerSec = 0.5 })
	key := map[string]string{"X-API-Key": "tenant-a"}
	for i := range 3 {
		if rec := do(h, "GET", "/api/orders/1", "", key); rec.Code != http.StatusOK {
			t.Fatalf("request %d: status %d, want 200", i, rec.Code)
		}
	}
	rec := do(h, "GET", "/api/orders/1", "", key)
	if rec.Code != http.StatusTooManyRequests {
		t.Fatalf("status = %d, want 429", rec.Code)
	}
	if got := rec.Header().Get("Retry-After"); got != "2" {
		t.Fatalf("Retry-After = %q, want 2 (1 token at 0.5/s)", got)
	}

	other := do(h, "GET", "/api/orders/1", "", map[string]string{"X-API-Key": "tenant-b"})
	if other.Code != http.StatusOK {
		t.Fatalf("tenant-b status = %d, want 200 (isolated bucket)", other.Code)
	}

	clock.Advance(2 * time.Second)
	if rec := do(h, "GET", "/api/orders/1", "", key); rec.Code != http.StatusOK {
		t.Fatalf("after refill status = %d, want 200", rec.Code)
	}
}

func TestHealthzBypassesRateLimit(t *testing.T) {
	h, _, _ := newTestGateway(t, func(c *Config) { c.RateCapacity = 1; c.RatePerSec = 0.001 })
	for i := range 20 {
		if rec := do(h, "GET", "/healthz", "", nil); rec.Code != http.StatusOK {
			t.Fatalf("healthz %d status = %d", i, rec.Code)
		}
	}
}

func TestRequestIDPropagatedAndGenerated(t *testing.T) {
	h, _, _ := newTestGateway(t, nil)
	rec := do(h, "GET", "/healthz", "", map[string]string{"X-Request-ID": "abc123"})
	if got := rec.Header().Get("X-Request-ID"); got != "abc123" {
		t.Fatalf("X-Request-ID = %q, want upstream value", got)
	}
	rec = do(h, "GET", "/healthz", "", nil)
	if got := rec.Header().Get("X-Request-ID"); len(got) != 16 {
		t.Fatalf("generated X-Request-ID = %q, want 16 hex chars", got)
	}
}

func TestPanicRecoveredAs500(t *testing.T) {
	h, _, _ := newTestGateway(t, nil)
	rec := do(h, "GET", "/debug/panic", "", map[string]string{"X-Request-ID": "trace-1"})
	if rec.Code != http.StatusInternalServerError {
		t.Fatalf("status = %d, want 500", rec.Code)
	}
	var body map[string]string
	if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
		t.Fatalf("body not JSON: %v (%q)", err, rec.Body.String())
	}
	if body["request_id"] != "trace-1" {
		t.Fatalf("request_id = %q, want trace-1", body["request_id"])
	}
	if rec := do(h, "GET", "/healthz", "", nil); rec.Code != http.StatusOK {
		t.Fatal("gateway must keep serving after a panic")
	}
}

func TestSlowRequestTimesOut(t *testing.T) {
	h, _, _ := newTestGateway(t, nil)
	start := time.Now()
	rec := do(h, "GET", "/api/slow", "", nil)
	if rec.Code != http.StatusServiceUnavailable {
		t.Fatalf("status = %d, want 503", rec.Code)
	}
	if elapsed := time.Since(start); elapsed > time.Second {
		t.Fatalf("timeout took %v, should cut off near 100ms", elapsed)
	}
}

func TestCreateOrderValidation(t *testing.T) {
	h, _, _ := newTestGateway(t, func(c *Config) { c.MaxBodyBytes = 64 })
	cases := []struct {
		name string
		body string
		want int
	}{
		{"malformed", `{"customer":`, http.StatusBadRequest},
		{"unknown field", `{"customer":"a","amount_cents":1,"admin":true}`, http.StatusBadRequest},
		{"business rule", `{"customer":"  ","amount_cents":10}`, http.StatusUnprocessableEntity},
		{"too large", `{"customer":"` + strings.Repeat("x", 200) + `","amount_cents":1}`, http.StatusRequestEntityTooLarge},
		{"valid", `{"customer":"globex","amount_cents":1250}`, http.StatusCreated},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			rec := do(h, "POST", "/api/orders", tc.body, map[string]string{"X-API-Key": tc.name})
			if rec.Code != tc.want {
				t.Fatalf("status = %d, want %d (body=%s)", rec.Code, tc.want, rec.Body.String())
			}
		})
	}
}

func TestMethodNotAllowed(t *testing.T) {
	h, _, _ := newTestGateway(t, nil)
	if rec := do(h, "DELETE", "/api/orders/1", "", nil); rec.Code != http.StatusMethodNotAllowed {
		t.Fatalf("status = %d, want 405", rec.Code)
	}
}

func TestEvictIdleClients(t *testing.T) {
	clock := &fakeClock{t: time.Unix(0, 0)}
	l := NewClientLimiter(5, 1, time.Minute, clock.Now)
	l.Allow("a")
	clock.Advance(30 * time.Second)
	l.Allow("b")
	clock.Advance(45 * time.Second)
	if removed := l.Evict(); removed != 1 {
		t.Fatalf("evicted %d, want 1 (only 'a' idle > 1m)", removed)
	}
	if l.Len() != 1 {
		t.Fatalf("Len = %d, want 1", l.Len())
	}
}

func TestConcurrentClientsAreRaceFree(t *testing.T) {
	h, _, _ := newTestGateway(t, func(c *Config) { c.RateCapacity = 50; c.RatePerSec = 1 })
	var wg sync.WaitGroup
	var mu sync.Mutex
	codes := map[int]int{}
	for i := range 100 {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			rec := do(h, "GET", "/api/orders/1", "", map[string]string{"X-API-Key": "shared"})
			mu.Lock()
			codes[rec.Code]++
			mu.Unlock()
		}(i)
	}
	wg.Wait()
	if codes[http.StatusOK] != 50 || codes[http.StatusTooManyRequests] != 50 {
		t.Fatalf("codes = %v, want exactly 50x200 and 50x429", codes)
	}
}
