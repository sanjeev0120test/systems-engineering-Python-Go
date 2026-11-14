package main

import (
	"math"
	"testing"
	"time"
)

var t0 = time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)

// series emits one event every step over [now-span, now]; isErr decides failures.
func series(now time.Time, span, step time.Duration, isErr func(at time.Time, i int) bool) []Event {
	var out []Event
	i := 0
	for at := now.Add(-span); !at.After(now); at = at.Add(step) {
		out = append(out, Event{At: at, Error: isErr(at, i), LatencyMs: 10})
		i++
	}
	return out
}

func approx(a, b float64) bool { return math.Abs(a-b) < 1e-9 }

func TestBurnRate(t *testing.T) {
	slo := SLO{Target: 0.999}
	if !approx(slo.ErrorBudget(), 0.001) {
		t.Fatalf("budget = %v", slo.ErrorBudget())
	}
	if got := slo.BurnRate(0.0144); !approx(got, 14.4) {
		t.Fatalf("burn = %v, want 14.4", got)
	}
	if !math.IsInf(SLO{Target: 1}.BurnRate(0.1), 1) {
		t.Fatal("100% SLO has zero budget: any error is infinite burn")
	}
}

func TestErrorRateWindowBoundaries(t *testing.T) {
	now := t0
	events := []Event{
		{At: now.Add(-10 * time.Minute), Error: true}, // exactly on boundary: excluded
		{At: now.Add(-9 * time.Minute), Error: true},
		{At: now.Add(-1 * time.Minute)},
		{At: now},
		{At: now.Add(time.Minute), Error: true}, // future: excluded
	}
	rate, n := ErrorRate(events, now, 10*time.Minute)
	if n != 3 || !approx(rate, 1.0/3) {
		t.Fatalf("rate=%v n=%d, want 1/3 over 3 events", rate, n)
	}
	if rate, n := ErrorRate(nil, now, time.Hour); rate != 0 || n != 0 {
		t.Fatal("empty window must be 0/0, not NaN")
	}
}

func TestFastBurnPagesDuringActiveIncident(t *testing.T) {
	now := t0
	events := series(now, 6*time.Hour, 10*time.Second, func(at time.Time, i int) bool {
		return at.After(now.Add(-time.Hour)) && i%25 == 0 // 4% errors in the last hour
	})
	alerts := EvaluateBurn(events, now, SLO{Target: 0.999}, DefaultBurnRules())
	byName := map[string]BurnAlert{}
	for _, a := range alerts {
		byName[a.Rule.Name] = a
	}
	if !byName["fast-burn"].Firing {
		t.Fatalf("fast-burn should page: %+v", byName["fast-burn"])
	}
	if !byName["medium-burn"].Firing {
		t.Fatalf("medium-burn should page (6h avg ~0.67%% = 6.7x): %+v", byName["medium-burn"])
	}
}

func TestShortWindowSilencesRecoveredIncident(t *testing.T) {
	now := t0
	events := series(now, 6*time.Hour, 10*time.Second, func(at time.Time, i int) bool {
		inIncident := at.After(now.Add(-time.Hour)) && at.Before(now.Add(-10*time.Minute))
		return inIncident && i%25 == 0
	})
	for _, a := range EvaluateBurn(events, now, SLO{Target: 0.999}, DefaultBurnRules()) {
		if a.Rule.Name == "fast-burn" {
			if a.LongBurn < a.Rule.Threshold {
				t.Fatalf("long window should still be hot: %+v", a)
			}
			if a.Firing {
				t.Fatalf("recovered incident must not keep paging: %+v", a)
			}
		}
	}
}

func TestBudgetRemaining(t *testing.T) {
	now := t0
	// 3601 events; the first sits on the excluded window boundary, so 2 errors / 3600.
	events := series(now, time.Hour, time.Second, func(_ time.Time, i int) bool { return i%2000 == 1 })
	got := BudgetRemaining(events, now, time.Hour, SLO{Target: 0.999})
	if want := 1 - (2.0/3600)/0.001; math.Abs(got-want) > 1e-9 {
		t.Fatalf("remaining = %v, want %v", got, want)
	}
	if BudgetRemaining(nil, now, time.Hour, SLO{Target: 0.999}) != 1 {
		t.Fatal("no traffic means no budget spent")
	}
}

func TestPercentileNearestRank(t *testing.T) {
	var v []float64
	for i := 100; i >= 1; i-- {
		v = append(v, float64(i))
	}
	cases := map[float64]float64{50: 50, 90: 90, 99: 99, 100: 100, 0: 1}
	for p, want := range cases {
		if got := Percentile(v, p); got != want {
			t.Fatalf("p%v = %v, want %v", p, got, want)
		}
	}
	if v[0] != 100 {
		t.Fatal("Percentile must not reorder the caller's slice")
	}
	if Percentile(nil, 99) != 0 {
		t.Fatal("empty input")
	}
}

func cohort(n, errs int, latency func(i int) float64) []Event {
	out := make([]Event, n)
	for i := range out {
		out[i] = Event{At: t0, Error: i < errs, LatencyMs: latency(i)}
	}
	return out
}

func flat(ms float64) func(int) float64 { return func(int) float64 { return ms } }

func TestCanaryPromoteWhenEquivalent(t *testing.T) {
	r := AnalyzeCanary(cohort(1000, 4, flat(50)), cohort(1000, 5, flat(52)), DefaultCanaryConfig())
	if r.Verdict != Promote {
		t.Fatalf("verdict = %s reasons=%v", r.Verdict, r.Reasons)
	}
}

func TestCanaryRollbackOnSignificantErrors(t *testing.T) {
	r := AnalyzeCanary(cohort(2000, 6, flat(50)), cohort(2000, 60, flat(50)), DefaultCanaryConfig())
	if r.Verdict != Rollback || r.ZScore < 2.33 {
		t.Fatalf("verdict = %s z=%.2f reasons=%v", r.Verdict, r.ZScore, r.Reasons)
	}
}

func TestCanaryHoldsOnNoisyErrorSpike(t *testing.T) {
	cfg := DefaultCanaryConfig()
	cfg.MinRequests = 100
	// 3/150 vs 0/150 exceeds the 0.5% floor but is not statistically significant.
	r := AnalyzeCanary(cohort(150, 0, flat(50)), cohort(150, 3, flat(50)), cfg)
	if r.Verdict != Hold {
		t.Fatalf("verdict = %s z=%.2f reasons=%v", r.Verdict, r.ZScore, r.Reasons)
	}
}

func TestCanaryRollbackOnTailLatency(t *testing.T) {
	baseline := cohort(1000, 0, flat(50))
	canary := cohort(1000, 0, func(i int) float64 {
		if i%50 == 0 {
			return 900 // 2% of requests hit a slow path → p99 explodes, p50 unchanged
		}
		return 50
	})
	r := AnalyzeCanary(baseline, canary, DefaultCanaryConfig())
	if r.Verdict != Rollback || r.Canary.P50Ms != 50 {
		t.Fatalf("verdict = %s canary=%+v reasons=%v", r.Verdict, r.Canary, r.Reasons)
	}
}

func TestCanaryHoldOnInsufficientTraffic(t *testing.T) {
	r := AnalyzeCanary(cohort(1000, 0, flat(50)), cohort(10, 10, flat(5000)), DefaultCanaryConfig())
	if r.Verdict != Hold {
		t.Fatalf("verdict = %s: never judge on 10 requests", r.Verdict)
	}
}

func TestTwoProportionZ(t *testing.T) {
	z := TwoProportionZ(Cohort{Requests: 1000, Errors: 10, ErrorRate: 0.01}, Cohort{Requests: 1000, Errors: 30, ErrorRate: 0.03})
	if z < 3.1 || z > 3.3 {
		t.Fatalf("z = %.3f, want ≈3.19", z)
	}
	if TwoProportionZ(Cohort{Requests: 10}, Cohort{Requests: 10}) != 0 {
		t.Fatal("zero errors on both sides has zero variance: z must be 0, not NaN")
	}
}
