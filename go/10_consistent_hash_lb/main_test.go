package main

import (
	"context"
	"io"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func ringWith(nodes ...string) *Ring {
	r := NewRing(200)
	for _, n := range nodes {
		r.Add(n)
	}
	return r
}

func owners(r *Ring, n int) map[string]string {
	out := make(map[string]string, n)
	for i := range n {
		k := "key-" + strconv.Itoa(i)
		out[k], _ = r.Get(k)
	}
	return out
}

func TestEvenDistribution(t *testing.T) {
	r := ringWith("a", "b", "c")
	counts := map[string]int{}
	for _, node := range owners(r, 30000) {
		counts[node]++
	}
	for node, c := range counts {
		share := float64(c) / 30000
		if share < 0.25 || share > 0.42 {
			t.Fatalf("node %s share = %.3f, want ~0.333 (counts=%v)", node, share, counts)
		}
	}
}

func TestAddingNodeMovesOnlyItsShare(t *testing.T) {
	r := ringWith("a", "b", "c")
	before := owners(r, 20000)
	r.Add("d")
	after := owners(r, 20000)
	moved := 0
	for k, old := range before {
		if after[k] != old {
			moved++
			if after[k] != "d" {
				t.Fatalf("key %s moved %s -> %s; keys may only move to the new node", k, old, after[k])
			}
		}
	}
	if frac := float64(moved) / 20000; frac < 0.15 || frac > 0.35 {
		t.Fatalf("moved fraction = %.3f, want ~0.25", frac)
	}
}

func TestRemovingNodeOnlyMovesItsKeys(t *testing.T) {
	r := ringWith("a", "b", "c", "d")
	before := owners(r, 10000)
	r.Remove("b")
	for k, node := range owners(r, 10000) {
		if before[k] != "b" && node != before[k] {
			t.Fatalf("key %s owned by %s moved to %s although only b was removed", k, before[k], node)
		}
		if node == "b" {
			t.Fatal("removed node still receives keys")
		}
	}
	if got := r.Nodes(); strings.Join(got, ",") != "a,c,d" {
		t.Fatalf("Nodes = %v", got)
	}
}

func TestUnhealthyNodeSkippedAndRestored(t *testing.T) {
	r := ringWith("a", "b", "c")
	before := owners(r, 5000)
	r.SetHealthy("a", false)
	during := owners(r, 5000)
	for k, node := range during {
		if node == "a" {
			t.Fatal("unhealthy node must not receive traffic")
		}
		if before[k] != "a" && node != before[k] {
			t.Fatalf("healthy user %s was reshuffled", k)
		}
	}
	r.SetHealthy("a", true)
	for k, node := range owners(r, 5000) {
		if node != before[k] {
			t.Fatalf("key %s did not return to original owner after recovery", k)
		}
	}
}

func TestGetNDistinctHealthyReplicas(t *testing.T) {
	r := ringWith("a", "b", "c", "d")
	r.SetHealthy("c", false)
	for i := range 200 {
		got := r.GetN("k"+strconv.Itoa(i), 3)
		if len(got) != 3 {
			t.Fatalf("GetN = %v, want 3 replicas", got)
		}
		seen := map[string]bool{}
		for _, n := range got {
			if seen[n] || n == "c" {
				t.Fatalf("GetN = %v: replicas must be distinct and healthy", got)
			}
			seen[n] = true
		}
	}
	if got := r.GetN("k", 10); len(got) != 3 {
		t.Fatalf("asking for more replicas than healthy nodes returns all healthy: %v", got)
	}
}

func TestEmptyAndAllDownRing(t *testing.T) {
	r := NewRing(10)
	if _, ok := r.Get("x"); ok {
		t.Fatal("empty ring must report no owner")
	}
	r.Add("a")
	r.Add("a")
	r.SetHealthy("a", false)
	if _, ok := r.Get("x"); ok {
		t.Fatal("all-down ring must report no owner")
	}
}

func toggleServer(up *atomic.Bool) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !up.Load() {
			w.WriteHeader(http.StatusServiceUnavailable)
			return
		}
		_, _ = io.WriteString(w, "ok")
	}))
}

func TestHealthCheckerHysteresis(t *testing.T) {
	var up atomic.Bool
	up.Store(true)
	srv := toggleServer(&up)
	defer srv.Close()

	r := ringWith("a")
	var changes []string
	hc := NewHealthChecker(r, map[string]string{"a": srv.URL}, 3, 2, time.Second)
	hc.OnChange = func(node string, healthy bool) { changes = append(changes, node+"="+strconv.FormatBool(healthy)) }
	ctx := context.Background()

	up.Store(false)
	hc.CheckOnce(ctx)
	hc.CheckOnce(ctx)
	if !r.IsHealthy("a") {
		t.Fatal("2 failures < fall=3: must stay healthy")
	}
	up.Store(true)
	hc.CheckOnce(ctx) // success resets the failure streak
	up.Store(false)
	hc.CheckOnce(ctx)
	hc.CheckOnce(ctx)
	if !r.IsHealthy("a") {
		t.Fatal("failure streak should have been reset by the success")
	}
	hc.CheckOnce(ctx)
	if r.IsHealthy("a") {
		t.Fatal("3 consecutive failures must mark node down")
	}
	up.Store(true)
	hc.CheckOnce(ctx)
	if r.IsHealthy("a") {
		t.Fatal("1 success < rise=2: must stay down")
	}
	hc.CheckOnce(ctx)
	if !r.IsHealthy("a") {
		t.Fatal("2 successes must bring node back")
	}
	if strings.Join(changes, ",") != "a=false,a=true" {
		t.Fatalf("changes = %v", changes)
	}
}

func TestHealthCheckerTimeoutCountsAsFailure(t *testing.T) {
	slow := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		select {
		case <-r.Context().Done():
		case <-time.After(2 * time.Second):
		}
	}))
	defer slow.Close()
	r := ringWith("a")
	hc := NewHealthChecker(r, map[string]string{"a": slow.URL}, 1, 1, 50*time.Millisecond)
	hc.CheckOnce(context.Background())
	if r.IsHealthy("a") {
		t.Fatal("a hung health endpoint must be treated as down")
	}
}

func TestRouterStickyFailoverAndAllDown(t *testing.T) {
	mk := func(name string) *httptest.Server {
		return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			_, _ = io.WriteString(w, name)
		}))
	}
	a, b, c := mk("a"), mk("b"), mk("c")
	defer a.Close()
	defer b.Close()
	defer c.Close()

	ring := NewRing(160)
	rt, err := NewRouter(ring, map[string]string{"a": a.URL, "b": b.URL, "c": c.URL})
	if err != nil {
		t.Fatal(err)
	}
	get := func(user string) (int, string, string) {
		req := httptest.NewRequest(http.MethodGet, "/x", nil)
		req.Header.Set("X-User-ID", user)
		rec := httptest.NewRecorder()
		rt.ServeHTTP(rec, req)
		return rec.Code, rec.Body.String(), rec.Header().Get("X-Backend")
	}

	_, first, hdr := get("alice")
	if first != hdr {
		t.Fatalf("body %q != X-Backend %q", first, hdr)
	}
	for range 10 {
		if _, body, _ := get("alice"); body != first {
			t.Fatalf("alice bounced from %s to %s", first, body)
		}
	}

	ring.SetHealthy(first, false)
	code, failover, _ := get("alice")
	if code != http.StatusOK || failover == first {
		t.Fatalf("failover code=%d backend=%s", code, failover)
	}

	for _, n := range ring.Nodes() {
		ring.SetHealthy(n, false)
	}
	if code, _, _ := get("alice"); code != http.StatusServiceUnavailable {
		t.Fatalf("all down: code=%d, want 503", code)
	}
}

func TestRouterBadGatewayWhenBackendUnreachable(t *testing.T) {
	dead := httptest.NewServer(http.NotFoundHandler())
	deadURL := dead.URL
	dead.Close()

	rt, err := NewRouter(NewRing(10), map[string]string{"dead": deadURL})
	if err != nil {
		t.Fatal(err)
	}
	rec := httptest.NewRecorder()
	rt.ServeHTTP(rec, httptest.NewRequest(http.MethodGet, "/", nil))
	if rec.Code != http.StatusBadGateway {
		t.Fatalf("code = %d, want 502 before health checks catch up", rec.Code)
	}
}
