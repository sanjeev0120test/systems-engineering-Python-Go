package main

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func fastConfig() Config {
	return Config{
		Workers:     4,
		QueueSize:   100,
		MaxAttempts: 3,
		JobTimeout:  200 * time.Millisecond,
		RetryDelay:  func(int) time.Duration { return time.Millisecond },
	}
}

func drain(t *testing.T, q *Queue) {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := q.Shutdown(ctx); err != nil {
		t.Fatalf("Shutdown: %v", err)
	}
}

func TestAllJobsProcessedOnGracefulShutdown(t *testing.T) {
	var done atomic.Int64
	q := New(fastConfig(), map[string]Handler{
		"work": func(ctx context.Context, j Job) error {
			time.Sleep(2 * time.Millisecond)
			done.Add(1)
			return nil
		},
	})
	for i := range 50 {
		if err := q.Enqueue(Job{ID: fmt.Sprint(i), Type: "work"}); err != nil {
			t.Fatal(err)
		}
	}
	drain(t, q)
	if done.Load() != 50 || q.Stats().Succeeded != 50 {
		t.Fatalf("done=%d stats=%+v, want all 50 processed before shutdown returns", done.Load(), q.Stats())
	}
	if err := q.Enqueue(Job{Type: "work"}); !errors.Is(err, ErrShuttingDown) {
		t.Fatalf("enqueue after shutdown err = %v", err)
	}
}

func TestIdempotencyKeyRejectsDuplicates(t *testing.T) {
	var charges atomic.Int64
	q := New(fastConfig(), map[string]Handler{
		"charge": func(context.Context, Job) error { charges.Add(1); return nil },
	})
	if err := q.Enqueue(Job{Type: "charge", IdempotencyKey: "order-1"}); err != nil {
		t.Fatal(err)
	}
	if err := q.Enqueue(Job{Type: "charge", IdempotencyKey: "order-1"}); !errors.Is(err, ErrDuplicate) {
		t.Fatalf("err = %v, want ErrDuplicate", err)
	}
	drain(t, q)
	if charges.Load() != 1 || q.Stats().Duplicates != 1 {
		t.Fatalf("charges=%d stats=%+v: customer must be charged exactly once", charges.Load(), q.Stats())
	}
}

func TestRetryThenSucceed(t *testing.T) {
	var attemptsSeen atomic.Int64
	q := New(fastConfig(), map[string]Handler{
		"flaky": func(_ context.Context, j Job) error {
			attemptsSeen.Store(int64(j.Attempts))
			if j.Attempts < 3 {
				return errors.New("transient")
			}
			return nil
		},
	})
	_ = q.Enqueue(Job{Type: "flaky"})
	drain(t, q)
	s := q.Stats()
	if s.Succeeded != 1 || s.Retried != 2 || s.DeadLettered != 0 || attemptsSeen.Load() != 3 {
		t.Fatalf("stats=%+v attempts=%d", s, attemptsSeen.Load())
	}
}

func TestExhaustedAndPermanentGoToDLQ(t *testing.T) {
	q := New(fastConfig(), map[string]Handler{
		"down":    func(context.Context, Job) error { return errors.New("connection refused") },
		"invalid": func(context.Context, Job) error { return Permanent(errors.New("bad payload")) },
	})
	_ = q.Enqueue(Job{ID: "a", Type: "down"})
	_ = q.Enqueue(Job{ID: "b", Type: "invalid"})
	drain(t, q)

	got := map[string]Job{}
	for _, j := range q.DeadLetters() {
		got[j.ID] = j
	}
	if got["a"].Attempts != 3 || got["a"].LastError != "connection refused" {
		t.Fatalf("exhausted job = %+v, want 3 attempts", got["a"])
	}
	if got["b"].Attempts != 1 {
		t.Fatalf("permanent job = %+v, want 1 attempt (no retries)", got["b"])
	}
}

func TestPanicIsolatedFromWorker(t *testing.T) {
	var ok atomic.Int64
	q := New(Config{Workers: 1, MaxAttempts: 1, RetryDelay: func(int) time.Duration { return 0 }}, map[string]Handler{
		"bad":  func(context.Context, Job) error { panic("nil pointer") },
		"good": func(context.Context, Job) error { ok.Add(1); return nil },
	})
	_ = q.Enqueue(Job{ID: "p", Type: "bad"})
	_ = q.Enqueue(Job{ID: "g", Type: "good"})
	drain(t, q)
	dlq := q.DeadLetters()
	if ok.Load() != 1 || len(dlq) != 1 || !strings.Contains(dlq[0].LastError, "handler panic") {
		t.Fatalf("ok=%d dlq=%+v: single worker must survive the panic", ok.Load(), dlq)
	}
}

func TestJobTimeoutCancelsHandler(t *testing.T) {
	cfg := fastConfig()
	cfg.JobTimeout = 20 * time.Millisecond
	cfg.MaxAttempts = 1
	q := New(cfg, map[string]Handler{
		"hang": func(ctx context.Context, _ Job) error { <-ctx.Done(); return ctx.Err() },
	})
	_ = q.Enqueue(Job{Type: "hang"})
	drain(t, q)
	dlq := q.DeadLetters()
	if len(dlq) != 1 || dlq[0].LastError != context.DeadlineExceeded.Error() {
		t.Fatalf("dlq = %+v, want deadline exceeded", dlq)
	}
}

func TestBackpressureWhenFull(t *testing.T) {
	started := make(chan struct{})
	release := make(chan struct{})
	q := New(Config{Workers: 1, QueueSize: 1}, map[string]Handler{
		"block": func(context.Context, Job) error {
			started <- struct{}{}
			<-release
			return nil
		},
	})
	if err := q.Enqueue(Job{Type: "block"}); err != nil {
		t.Fatal(err)
	}
	<-started
	if err := q.Enqueue(Job{Type: "block"}); err != nil {
		t.Fatalf("buffer slot should accept: %v", err)
	}
	if err := q.Enqueue(Job{Type: "block", IdempotencyKey: "k"}); !errors.Is(err, ErrQueueFull) {
		t.Fatalf("err = %v, want ErrQueueFull", err)
	}
	close(release)
	go func() { <-started }()
	drain(t, q)
	if err := q.Enqueue(Job{Type: "block", IdempotencyKey: "k"}); !errors.Is(err, ErrShuttingDown) {
		t.Fatalf("err = %v", err)
	}
	if q.Stats().Succeeded != 2 {
		t.Fatalf("stats = %+v", q.Stats())
	}
}

func TestRejectedKeyCanBeRetriedLater(t *testing.T) {
	started := make(chan struct{})
	release := make(chan struct{})
	q := New(Config{Workers: 1, QueueSize: 1}, map[string]Handler{
		"block": func(context.Context, Job) error { started <- struct{}{}; <-release; return nil },
	})
	_ = q.Enqueue(Job{Type: "block"})
	<-started
	_ = q.Enqueue(Job{Type: "block"})
	if err := q.Enqueue(Job{Type: "block", IdempotencyKey: "retry-me"}); !errors.Is(err, ErrQueueFull) {
		t.Fatal(err)
	}
	close(release)
	<-started
	deadline := time.Now().Add(2 * time.Second)
	var err error
	for time.Now().Before(deadline) {
		if err = q.Enqueue(Job{Type: "block", IdempotencyKey: "retry-me"}); !errors.Is(err, ErrQueueFull) {
			break
		}
		time.Sleep(time.Millisecond)
	}
	if err != nil {
		t.Fatalf("a key rejected for backpressure must not be marked seen: %v", err)
	}
	go func() { <-started }()
	drain(t, q)
}

func TestUnknownJobType(t *testing.T) {
	q := New(fastConfig(), map[string]Handler{})
	if err := q.Enqueue(Job{Type: "nope"}); !errors.Is(err, ErrUnknownJobType) {
		t.Fatalf("err = %v", err)
	}
	drain(t, q)
}

func TestShutdownDeadlineMovesUnfinishedToDLQ(t *testing.T) {
	cfg := fastConfig()
	cfg.Workers = 1
	cfg.JobTimeout = time.Hour
	q := New(cfg, map[string]Handler{
		"slow": func(ctx context.Context, _ Job) error { <-ctx.Done(); return ctx.Err() },
	})
	for i := range 5 {
		_ = q.Enqueue(Job{ID: fmt.Sprint(i), Type: "slow"})
	}
	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
	defer cancel()
	if err := q.Shutdown(ctx); !errors.Is(err, context.DeadlineExceeded) {
		t.Fatalf("err = %v, want DeadlineExceeded", err)
	}
	if n := len(q.DeadLetters()); n != 5 {
		t.Fatalf("dlq size = %d, want all 5 unfinished jobs preserved", n)
	}
}

func TestExponentialDelay(t *testing.T) {
	d := ExponentialDelay(100*time.Millisecond, time.Second)
	want := []time.Duration{100, 200, 400, 800, 1000, 1000}
	for i, w := range want {
		if got := d(i + 1); got != w*time.Millisecond {
			t.Fatalf("attempt %d delay = %v, want %vms", i+1, got, w)
		}
	}
}
