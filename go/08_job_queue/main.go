// Step 39 — Background job queue: idempotency keys, backpressure, retries with
// backoff, dead-letter queue, per-job timeouts, panic isolation, graceful drain.
//
// Java analogy: SQS/JMS consumer with a bounded ThreadPoolExecutor + DLQ.
package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

var (
	ErrDuplicate      = errors.New("duplicate job: idempotency key already accepted")
	ErrQueueFull      = errors.New("queue full")
	ErrShuttingDown   = errors.New("queue is shutting down")
	ErrUnknownJobType = errors.New("no handler registered for job type")
)

type permanentError struct{ err error }

func (p *permanentError) Error() string { return p.err.Error() }
func (p *permanentError) Unwrap() error { return p.err }

// Permanent marks a failure that retrying cannot fix (validation, bad payload).
func Permanent(err error) error { return &permanentError{err: err} }

// IsPermanent reports whether err was marked Permanent.
func IsPermanent(err error) bool {
	var p *permanentError
	return errors.As(err, &p)
}

// Job is one unit of background work.
type Job struct {
	ID             string
	Type           string
	IdempotencyKey string
	Payload        map[string]string
	Attempts       int
	LastError      string
}

// Handler processes one job. It must honor ctx cancellation.
type Handler func(ctx context.Context, job Job) error

// Config tunes the queue.
type Config struct {
	Workers     int
	QueueSize   int
	MaxAttempts int
	JobTimeout  time.Duration
	RetryDelay  func(attempt int) time.Duration
	// DedupTTL bounds idempotency memory: keys older than this are forgotten,
	// so it must exceed the longest window in which a producer may redeliver.
	DedupTTL time.Duration
	Now      func() time.Time
}

const dedupSweepEvery = 1024

// ExponentialDelay returns base*2^(attempt-1), capped at max.
func ExponentialDelay(base, max time.Duration) func(int) time.Duration {
	return func(attempt int) time.Duration {
		d := base
		for i := 1; i < attempt && d < max; i++ {
			d *= 2
		}
		if d > max {
			d = max
		}
		return d
	}
}

// Stats is a point-in-time snapshot of queue counters.
type Stats struct {
	Enqueued, Succeeded, Retried, DeadLettered, Duplicates, Rejected int64
}

// Queue is an in-memory work queue with a fixed worker pool.
type Queue struct {
	cfg      Config
	handlers map[string]Handler
	jobs     chan Job

	ctx    context.Context
	cancel context.CancelFunc

	mu         sync.Mutex
	seen       map[string]time.Time
	sinceSweep int
	dlq        []Job
	closed     bool
	stopped    bool

	workers sync.WaitGroup
	pending sync.WaitGroup

	enqueued, succeeded, retried, deadLettered, duplicates, rejected atomic.Int64
}

// New starts cfg.Workers workers. handlers must not be mutated afterwards.
func New(cfg Config, handlers map[string]Handler) *Queue {
	if cfg.Workers <= 0 {
		cfg.Workers = 4
	}
	if cfg.QueueSize <= 0 {
		cfg.QueueSize = 100
	}
	if cfg.MaxAttempts <= 0 {
		cfg.MaxAttempts = 3
	}
	if cfg.JobTimeout <= 0 {
		cfg.JobTimeout = 30 * time.Second
	}
	if cfg.RetryDelay == nil {
		cfg.RetryDelay = ExponentialDelay(100*time.Millisecond, 10*time.Second)
	}
	if cfg.DedupTTL <= 0 {
		cfg.DedupTTL = 24 * time.Hour
	}
	if cfg.Now == nil {
		cfg.Now = time.Now
	}
	ctx, cancel := context.WithCancel(context.Background())
	q := &Queue{
		cfg:      cfg,
		handlers: handlers,
		jobs:     make(chan Job, cfg.QueueSize),
		ctx:      ctx,
		cancel:   cancel,
		seen:     make(map[string]time.Time),
	}
	for range cfg.Workers {
		q.workers.Add(1)
		go q.worker()
	}
	return q
}

// Enqueue accepts a job or rejects it immediately (never blocks the caller).
// ErrQueueFull is backpressure: an HTTP API would map it to 503 + Retry-After.
func (q *Queue) Enqueue(job Job) error {
	q.mu.Lock()
	defer q.mu.Unlock()
	if q.closed {
		q.rejected.Add(1)
		return ErrShuttingDown
	}
	if _, ok := q.handlers[job.Type]; !ok {
		q.rejected.Add(1)
		return fmt.Errorf("%w: %q", ErrUnknownJobType, job.Type)
	}
	now := q.cfg.Now()
	q.sweepSeen(now)
	if job.IdempotencyKey != "" {
		if at, dup := q.seen[job.IdempotencyKey]; dup && now.Sub(at) < q.cfg.DedupTTL {
			q.duplicates.Add(1)
			return ErrDuplicate
		}
	}
	q.pending.Add(1)
	select {
	case q.jobs <- job:
	default:
		q.pending.Done()
		q.rejected.Add(1)
		return ErrQueueFull
	}
	if job.IdempotencyKey != "" {
		q.seen[job.IdempotencyKey] = now
	}
	q.enqueued.Add(1)
	return nil
}

// sweepSeen amortizes expiry: one O(n) pass every dedupSweepEvery enqueues.
// Caller holds q.mu.
func (q *Queue) sweepSeen(now time.Time) {
	q.sinceSweep++
	if q.sinceSweep < dedupSweepEvery {
		return
	}
	q.sinceSweep = 0
	for key, at := range q.seen {
		if now.Sub(at) >= q.cfg.DedupTTL {
			delete(q.seen, key)
		}
	}
}

// TrackedKeys reports how many idempotency keys are held in memory.
func (q *Queue) TrackedKeys() int {
	q.mu.Lock()
	defer q.mu.Unlock()
	return len(q.seen)
}

func (q *Queue) worker() {
	defer q.workers.Done()
	for {
		select {
		case <-q.ctx.Done():
			return
		case job := <-q.jobs:
			q.process(job)
		}
	}
}

func (q *Queue) process(job Job) {
	job.Attempts++
	err := q.run(job)
	if err == nil {
		q.succeeded.Add(1)
		q.pending.Done()
		return
	}
	job.LastError = err.Error()
	if IsPermanent(err) || job.Attempts >= q.cfg.MaxAttempts || q.ctx.Err() != nil {
		q.deadLetter(job)
		return
	}
	q.retried.Add(1)
	time.AfterFunc(q.cfg.RetryDelay(job.Attempts), func() { q.requeue(job) })
}

func (q *Queue) run(job Job) (err error) {
	// Go cannot preempt a goroutine: the timeout only works if the handler watches ctx.
	ctx, cancel := context.WithTimeout(q.ctx, q.cfg.JobTimeout)
	defer cancel()
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("handler panic: %v", r)
		}
	}()
	return q.handlers[job.Type](ctx, job)
}

func (q *Queue) requeue(job Job) {
	q.mu.Lock()
	if q.stopped {
		q.mu.Unlock()
		job.LastError = "abandoned at shutdown before retry: " + job.LastError
		q.deadLetter(job)
		return
	}
	select {
	case q.jobs <- job:
		q.mu.Unlock()
	default:
		q.mu.Unlock()
		time.AfterFunc(10*time.Millisecond, func() { q.requeue(job) })
	}
}

func (q *Queue) deadLetter(job Job) {
	q.mu.Lock()
	q.dlq = append(q.dlq, job)
	q.mu.Unlock()
	q.deadLettered.Add(1)
	q.pending.Done()
}

// Shutdown stops intake, waits for in-flight and retrying jobs, then stops
// workers. If ctx expires first, in-flight jobs are cancelled and anything
// unfinished goes to the DLQ so it can be replayed — nothing is silently lost.
func (q *Queue) Shutdown(ctx context.Context) error {
	q.mu.Lock()
	q.closed = true
	q.mu.Unlock()

	drained := make(chan struct{})
	go func() {
		q.pending.Wait()
		close(drained)
	}()

	var err error
	select {
	case <-drained:
	case <-ctx.Done():
		err = ctx.Err()
	}
	q.cancel()
	q.workers.Wait()

	q.mu.Lock()
	q.stopped = true
	var leftover []Job
	for len(q.jobs) > 0 {
		job := <-q.jobs
		job.LastError = "abandoned at shutdown: never started"
		leftover = append(leftover, job)
	}
	q.mu.Unlock()
	for _, job := range leftover {
		q.deadLetter(job)
	}
	return err
}

// Stats returns current counters.
func (q *Queue) Stats() Stats {
	return Stats{
		Enqueued:     q.enqueued.Load(),
		Succeeded:    q.succeeded.Load(),
		Retried:      q.retried.Load(),
		DeadLettered: q.deadLettered.Load(),
		Duplicates:   q.duplicates.Load(),
		Rejected:     q.rejected.Load(),
	}
}

// DeadLetters returns a copy of the DLQ for inspection or replay.
func (q *Queue) DeadLetters() []Job {
	q.mu.Lock()
	defer q.mu.Unlock()
	return append([]Job(nil), q.dlq...)
}

func main() {
	fmt.Println("Step 39 — Job queue demo (idempotency, retries, DLQ, graceful drain)")

	var mu sync.Mutex
	var log []string
	record := func(format string, args ...any) {
		mu.Lock()
		log = append(log, fmt.Sprintf(format, args...))
		mu.Unlock()
	}

	handlers := map[string]Handler{
		"send_email": func(ctx context.Context, j Job) error {
			if j.Payload["flaky"] == "true" && j.Attempts < 3 {
				return fmt.Errorf("smtp 421 service not available (attempt %d)", j.Attempts)
			}
			record("email sent to %s after %d attempt(s)", j.Payload["to"], j.Attempts)
			return nil
		},
		"charge_card": func(ctx context.Context, j Job) error {
			if strings.HasPrefix(j.Payload["amount"], "-") {
				return Permanent(fmt.Errorf("invalid amount %s", j.Payload["amount"]))
			}
			select {
			case <-time.After(20 * time.Millisecond):
			case <-ctx.Done():
				return ctx.Err()
			}
			record("charged %s for order %s", j.Payload["amount"], j.Payload["order"])
			return nil
		},
		"render_report": func(ctx context.Context, j Job) error {
			if j.Payload["size"] == "huge" {
				<-ctx.Done()
				return fmt.Errorf("render aborted: %w", ctx.Err())
			}
			var cfg map[string]string
			if j.Payload["corrupt"] == "true" {
				cfg["template"] = "x" // nil map write — panics, worker survives
			}
			record("report %s rendered", j.ID)
			return nil
		},
	}

	q := New(Config{
		Workers:     3,
		QueueSize:   50,
		MaxAttempts: 3,
		JobTimeout:  150 * time.Millisecond,
		RetryDelay:  ExponentialDelay(20*time.Millisecond, 200*time.Millisecond),
	}, handlers)

	submit := func(j Job) {
		if err := q.Enqueue(j); err != nil {
			fmt.Printf("  enqueue %-10s rejected: %v\n", j.ID, err)
		}
	}
	submit(Job{ID: "pay-1001", Type: "charge_card", IdempotencyKey: "order-1001", Payload: map[string]string{"order": "1001", "amount": "49.99"}})
	submit(Job{ID: "pay-1001b", Type: "charge_card", IdempotencyKey: "order-1001", Payload: map[string]string{"order": "1001", "amount": "49.99"}})
	submit(Job{ID: "pay-1002", Type: "charge_card", IdempotencyKey: "order-1002", Payload: map[string]string{"order": "1002", "amount": "-5"}})
	submit(Job{ID: "mail-1", Type: "send_email", Payload: map[string]string{"to": "oncall@example.com", "flaky": "true"}})
	submit(Job{ID: "mail-2", Type: "send_email", Payload: map[string]string{"to": "cfo@example.com"}})
	submit(Job{ID: "rep-1", Type: "render_report", Payload: map[string]string{}})
	submit(Job{ID: "rep-2", Type: "render_report", Payload: map[string]string{"size": "huge"}})
	submit(Job{ID: "rep-3", Type: "render_report", Payload: map[string]string{"corrupt": "true"}})
	submit(Job{ID: "sms-1", Type: "send_sms"})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := q.Shutdown(ctx); err != nil {
		fmt.Fprintln(os.Stderr, "shutdown:", err)
		os.Exit(1)
	}
	if err := q.Enqueue(Job{ID: "late", Type: "send_email"}); err != nil {
		fmt.Printf("  enqueue late       rejected: %v\n", err)
	}

	fmt.Println("\nCompleted work:")
	for _, line := range log {
		fmt.Println("  " + line)
	}
	fmt.Println("\nDead-letter queue (replay candidates):")
	for _, j := range q.DeadLetters() {
		fmt.Printf("  %-8s type=%-13s attempts=%d error=%q\n", j.ID, j.Type, j.Attempts, j.LastError)
	}
	fmt.Printf("\nStats: %+v\n", q.Stats())
}
