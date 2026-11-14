// Step 40 — Release safety: SLO error-budget burn-rate alerts (multi-window,
// multi-burn-rate from the Google SRE Workbook) and automated canary analysis
// (promote / hold / rollback) with a statistical significance check.
//
// Java analogy: Spinnaker Kayenta canary judge + Prometheus burn-rate rules.
package main

import (
	"fmt"
	"math"
	"math/rand"
	"sort"
	"time"
)

// ---------------------------------------------------------------------------
// SLO burn rate
// ---------------------------------------------------------------------------

// Event is one request outcome.
type Event struct {
	At        time.Time
	Error     bool
	LatencyMs float64
}

// SLO is an availability objective, e.g. 0.999 = 99.9% of requests succeed.
type SLO struct{ Target float64 }

// ErrorBudget is the allowed failure fraction (0.001 for 99.9%).
func (s SLO) ErrorBudget() float64 { return 1 - s.Target }

// BurnRate is how many times faster than "exactly on budget" errors arrive.
// 1.0 spends the whole budget in the SLO period; 14.4 spends 2% of a 30-day
// budget in one hour.
func (s SLO) BurnRate(errorRate float64) float64 {
	budget := s.ErrorBudget()
	if budget <= 0 {
		return math.Inf(1)
	}
	return errorRate / budget
}

// ErrorRate over (now-window, now]. Returns rate and request count.
func ErrorRate(events []Event, now time.Time, window time.Duration) (float64, int) {
	start := now.Add(-window)
	total, errs := 0, 0
	for _, e := range events {
		if e.At.After(start) && !e.At.After(now) {
			total++
			if e.Error {
				errs++
			}
		}
	}
	if total == 0 {
		return 0, 0
	}
	return float64(errs) / float64(total), total
}

// BurnRule fires only when BOTH windows exceed the threshold: the long window
// proves the problem is significant, the short window proves it is still
// happening (so the alert resets quickly after recovery).
type BurnRule struct {
	Name        string
	Severity    string
	LongWindow  time.Duration
	ShortWindow time.Duration
	Threshold   float64
}

// DefaultBurnRules are the SRE Workbook recommendations for a 30-day SLO.
func DefaultBurnRules() []BurnRule {
	return []BurnRule{
		{Name: "fast-burn", Severity: "page", LongWindow: time.Hour, ShortWindow: 5 * time.Minute, Threshold: 14.4},
		{Name: "medium-burn", Severity: "page", LongWindow: 6 * time.Hour, ShortWindow: 30 * time.Minute, Threshold: 6},
		{Name: "slow-burn", Severity: "ticket", LongWindow: 3 * 24 * time.Hour, ShortWindow: 6 * time.Hour, Threshold: 1},
	}
}

// BurnAlert is one evaluated rule.
type BurnAlert struct {
	Rule      BurnRule
	LongBurn  float64
	ShortBurn float64
	Firing    bool
}

// EvaluateBurn evaluates every rule at time now.
func EvaluateBurn(events []Event, now time.Time, slo SLO, rules []BurnRule) []BurnAlert {
	out := make([]BurnAlert, 0, len(rules))
	for _, r := range rules {
		longRate, _ := ErrorRate(events, now, r.LongWindow)
		shortRate, _ := ErrorRate(events, now, r.ShortWindow)
		a := BurnAlert{Rule: r, LongBurn: slo.BurnRate(longRate), ShortBurn: slo.BurnRate(shortRate)}
		a.Firing = a.LongBurn >= r.Threshold && a.ShortBurn >= r.Threshold
		out = append(out, a)
	}
	return out
}

// BudgetRemaining is the fraction of the period's error budget left (can go negative).
func BudgetRemaining(events []Event, now time.Time, period time.Duration, slo SLO) float64 {
	rate, n := ErrorRate(events, now, period)
	if n == 0 {
		return 1
	}
	return 1 - rate/slo.ErrorBudget()
}

// ---------------------------------------------------------------------------
// Canary analysis
// ---------------------------------------------------------------------------

// Percentile uses the nearest-rank method on a copy of values.
func Percentile(values []float64, p float64) float64 {
	if len(values) == 0 {
		return 0
	}
	s := append([]float64(nil), values...)
	sort.Float64s(s)
	rank := int(math.Ceil(p / 100 * float64(len(s))))
	if rank < 1 {
		rank = 1
	}
	if rank > len(s) {
		rank = len(s)
	}
	return s[rank-1]
}

// Cohort summarises one deployment's traffic.
type Cohort struct {
	Requests  int
	Errors    int
	ErrorRate float64
	P50Ms     float64
	P99Ms     float64
}

// Summarize builds a Cohort from events.
func Summarize(events []Event) Cohort {
	c := Cohort{Requests: len(events)}
	lat := make([]float64, 0, len(events))
	for _, e := range events {
		if e.Error {
			c.Errors++
		}
		lat = append(lat, e.LatencyMs)
	}
	if c.Requests > 0 {
		c.ErrorRate = float64(c.Errors) / float64(c.Requests)
	}
	c.P50Ms = Percentile(lat, 50)
	c.P99Ms = Percentile(lat, 99)
	return c
}

// TwoProportionZ is the pooled z-score for canary error rate > baseline error rate.
func TwoProportionZ(baseline, canary Cohort) float64 {
	n1, n2 := float64(baseline.Requests), float64(canary.Requests)
	if n1 == 0 || n2 == 0 {
		return 0
	}
	pooled := float64(baseline.Errors+canary.Errors) / (n1 + n2)
	se := math.Sqrt(pooled * (1 - pooled) * (1/n1 + 1/n2))
	if se == 0 {
		return 0
	}
	return (canary.ErrorRate - baseline.ErrorRate) / se
}

// Verdict is the canary decision.
type Verdict string

const (
	Promote  Verdict = "PROMOTE"
	Hold     Verdict = "HOLD"
	Rollback Verdict = "ROLLBACK"
)

// CanaryConfig holds the judge's thresholds.
type CanaryConfig struct {
	MinRequests        int     // per cohort, below this we cannot judge
	MaxErrorRatio      float64 // canary error rate may be at most this × baseline
	ErrorRateFloor     float64 // ignore error-rate differences below this absolute rate
	MinZScore          float64 // significance required before rolling back on errors
	MaxP99LatencyRatio float64 // canary p99 may be at most this × baseline p99
	P99SlackMs         float64 // absolute latency slack so tiny p99s do not flap
}

// DefaultCanaryConfig is a conservative judge.
func DefaultCanaryConfig() CanaryConfig {
	return CanaryConfig{
		MinRequests:        500,
		MaxErrorRatio:      1.5,
		ErrorRateFloor:     0.005,
		MinZScore:          2.33, // ~99% one-sided
		MaxP99LatencyRatio: 1.2,
		P99SlackMs:         10,
	}
}

// CanaryReport explains the verdict.
type CanaryReport struct {
	Verdict  Verdict
	Reasons  []string
	Baseline Cohort
	Canary   Cohort
	ZScore   float64
}

// AnalyzeCanary compares canary traffic against a baseline running the old version
// at the same time (not against historical data, which hides time-of-day effects).
func AnalyzeCanary(baselineEvents, canaryEvents []Event, cfg CanaryConfig) CanaryReport {
	b, c := Summarize(baselineEvents), Summarize(canaryEvents)
	r := CanaryReport{Baseline: b, Canary: c, ZScore: TwoProportionZ(b, c)}

	if b.Requests < cfg.MinRequests || c.Requests < cfg.MinRequests {
		r.Verdict = Hold
		r.Reasons = append(r.Reasons, fmt.Sprintf("insufficient traffic: baseline=%d canary=%d (need %d each)", b.Requests, c.Requests, cfg.MinRequests))
		return r
	}

	regressed, suspicious := false, false

	allowedErr := math.Max(b.ErrorRate*cfg.MaxErrorRatio, cfg.ErrorRateFloor)
	if c.ErrorRate > allowedErr {
		if r.ZScore >= cfg.MinZScore {
			regressed = true
			r.Reasons = append(r.Reasons, fmt.Sprintf("error rate %.2f%% > allowed %.2f%% (z=%.2f, significant)", c.ErrorRate*100, allowedErr*100, r.ZScore))
		} else {
			suspicious = true
			r.Reasons = append(r.Reasons, fmt.Sprintf("error rate %.2f%% elevated but not significant (z=%.2f < %.2f): collect more traffic", c.ErrorRate*100, r.ZScore, cfg.MinZScore))
		}
	}

	allowedP99 := b.P99Ms*cfg.MaxP99LatencyRatio + cfg.P99SlackMs
	if c.P99Ms > allowedP99 {
		regressed = true
		r.Reasons = append(r.Reasons, fmt.Sprintf("p99 latency %.1fms > allowed %.1fms (baseline %.1fms)", c.P99Ms, allowedP99, b.P99Ms))
	}

	switch {
	case regressed:
		r.Verdict = Rollback
	case suspicious:
		r.Verdict = Hold
	default:
		r.Verdict = Promote
		r.Reasons = append(r.Reasons, "canary within error and latency thresholds")
	}
	return r
}

// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

func synth(rng *rand.Rand, n int, start time.Time, errRate, baseLatency, tailLatency, tailFrac float64) []Event {
	out := make([]Event, n)
	for i := range out {
		lat := baseLatency * (0.5 + rng.Float64())
		if rng.Float64() < tailFrac {
			lat = tailLatency * (0.8 + 0.4*rng.Float64())
		}
		out[i] = Event{At: start.Add(time.Duration(i) * time.Second), Error: rng.Float64() < errRate, LatencyMs: lat}
	}
	return out
}

func printReport(name string, r CanaryReport) {
	fmt.Printf("\n  %-22s verdict=%s z=%.2f\n", name, r.Verdict, r.ZScore)
	fmt.Printf("    baseline: n=%d err=%.2f%% p50=%.0fms p99=%.0fms\n", r.Baseline.Requests, r.Baseline.ErrorRate*100, r.Baseline.P50Ms, r.Baseline.P99Ms)
	fmt.Printf("    canary:   n=%d err=%.2f%% p50=%.0fms p99=%.0fms\n", r.Canary.Requests, r.Canary.ErrorRate*100, r.Canary.P50Ms, r.Canary.P99Ms)
	for _, reason := range r.Reasons {
		fmt.Println("    - " + reason)
	}
}

func main() {
	fmt.Println("Step 40 — SLO burn-rate alerting + automated canary analysis")
	rng := rand.New(rand.NewSource(42))
	now := time.Date(2026, 11, 14, 12, 0, 0, 0, time.UTC)
	slo := SLO{Target: 0.999}

	fmt.Println("\n[1] Error-budget burn (SLO 99.9%): healthy 6h, then a bad deploy 40 minutes ago")
	var events []Event
	for t := now.Add(-6 * time.Hour); !t.After(now); t = t.Add(2 * time.Second) {
		errRate := 0.0003
		if t.After(now.Add(-40 * time.Minute)) {
			errRate = 0.03
		}
		events = append(events, Event{At: t, Error: rng.Float64() < errRate})
	}
	for _, a := range EvaluateBurn(events, now, slo, DefaultBurnRules()) {
		state := "ok"
		if a.Firing {
			state = "FIRING -> " + a.Rule.Severity
		}
		fmt.Printf("  %-12s long(%-6s)=%5.1fx short(%-5s)=%5.1fx threshold=%4.1fx  %s\n",
			a.Rule.Name, a.Rule.LongWindow, a.LongBurn, a.Rule.ShortWindow, a.ShortBurn, a.Rule.Threshold, state)
	}
	fmt.Printf("  6h budget remaining: %.0f%%\n", BudgetRemaining(events, now, 6*time.Hour, slo)*100)

	fmt.Println("\n[2] Canary judge (baseline vs canary, same time window)")
	start := now.Add(-30 * time.Minute)
	cfg := DefaultCanaryConfig()
	baseline := synth(rng, 5000, start, 0.004, 40, 180, 0.02)
	printReport("healthy canary", AnalyzeCanary(baseline, synth(rng, 5000, start, 0.004, 41, 185, 0.02), cfg))
	printReport("noisy error blip", AnalyzeCanary(baseline, synth(rng, 600, start, 0.008, 40, 180, 0.02), cfg))
	printReport("error regression", AnalyzeCanary(baseline, synth(rng, 5000, start, 0.03, 40, 180, 0.02), cfg))
	printReport("latency regression", AnalyzeCanary(baseline, synth(rng, 5000, start, 0.004, 45, 600, 0.03), cfg))
	printReport("too little traffic", AnalyzeCanary(baseline, synth(rng, 120, start, 0.0, 40, 180, 0.02), cfg))
}
