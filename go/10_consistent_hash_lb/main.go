// Step 41 — Sticky load balancer: consistent hashing with virtual nodes,
// active health checks with rise/fall hysteresis, and a reverse proxy that
// fails over only the users whose backend died.
//
// Java analogy: Envoy ring-hash LB / HAProxy "balance hdr(X-User-ID)" + health checks.
package main

import (
	"context"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"net/http/httputil"
	"net/url"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// ---------------------------------------------------------------------------
// Consistent hash ring
// ---------------------------------------------------------------------------

func hash64(s string) uint64 {
	sum := sha256.Sum256([]byte(s))
	return binary.BigEndian.Uint64(sum[:8])
}

// Ring maps keys to nodes; adding or removing a node only moves ~1/N of keys.
type Ring struct {
	mu       sync.RWMutex
	replicas int
	hashes   []uint64
	owners   map[uint64]string
	healthy  map[string]bool
}

// NewRing creates a ring with `replicas` virtual nodes per real node. More
// virtual nodes means a more even spread (150–200 is a common default).
func NewRing(replicas int) *Ring {
	if replicas <= 0 {
		replicas = 160
	}
	return &Ring{replicas: replicas, owners: make(map[uint64]string), healthy: make(map[string]bool)}
}

// Add inserts a node (healthy by default). Adding an existing node is a no-op.
func (r *Ring) Add(node string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.healthy[node]; ok {
		return
	}
	r.healthy[node] = true
	for i := range r.replicas {
		h := hash64(node + "#" + strconv.Itoa(i))
		r.owners[h] = node
		r.hashes = append(r.hashes, h)
	}
	sort.Slice(r.hashes, func(i, j int) bool { return r.hashes[i] < r.hashes[j] })
}

// Remove deletes a node and its virtual nodes.
func (r *Ring) Remove(node string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.healthy[node]; !ok {
		return
	}
	delete(r.healthy, node)
	kept := r.hashes[:0]
	for _, h := range r.hashes {
		if r.owners[h] == node {
			delete(r.owners, h)
			continue
		}
		kept = append(kept, h)
	}
	r.hashes = kept
}

// SetHealthy marks a node up or down without moving anyone else's keys.
func (r *Ring) SetHealthy(node string, ok bool) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, exists := r.healthy[node]; exists {
		r.healthy[node] = ok
	}
}

// IsHealthy reports a node's health flag.
func (r *Ring) IsHealthy(node string) bool {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return r.healthy[node]
}

// Nodes returns all nodes, sorted.
func (r *Ring) Nodes() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	out := make([]string, 0, len(r.healthy))
	for n := range r.healthy {
		out = append(out, n)
	}
	sort.Strings(out)
	return out
}

// Get returns the healthy owner of key.
func (r *Ring) Get(key string) (string, bool) {
	nodes := r.GetN(key, 1)
	if len(nodes) == 0 {
		return "", false
	}
	return nodes[0], true
}

// GetN walks clockwise from key and returns up to n distinct healthy nodes —
// the primary plus replicas (how Cassandra/Dynamo place data copies).
func (r *Ring) GetN(key string, n int) []string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	if len(r.hashes) == 0 || n <= 0 {
		return nil
	}
	h := hash64(key)
	start := sort.Search(len(r.hashes), func(i int) bool { return r.hashes[i] >= h })
	seen := make(map[string]bool, n)
	out := make([]string, 0, n)
	for i := 0; i < len(r.hashes) && len(out) < n; i++ {
		node := r.owners[r.hashes[(start+i)%len(r.hashes)]]
		if seen[node] || !r.healthy[node] {
			continue
		}
		seen[node] = true
		out = append(out, node)
	}
	return out
}

// ---------------------------------------------------------------------------
// Active health checking
// ---------------------------------------------------------------------------

// HealthChecker probes backends and flips ring health with hysteresis:
// Fall consecutive failures mark a node down, Rise consecutive successes bring
// it back. This prevents one dropped packet from reshuffling users.
type HealthChecker struct {
	Ring     *Ring
	Client   *http.Client
	Targets  map[string]string
	Fall     int
	Rise     int
	OnChange func(node string, healthy bool)

	mu    sync.Mutex
	fails map[string]int
	oks   map[string]int
}

// NewHealthChecker builds a checker with a per-probe timeout.
func NewHealthChecker(ring *Ring, targets map[string]string, fall, rise int, timeout time.Duration) *HealthChecker {
	return &HealthChecker{
		Ring:    ring,
		Client:  &http.Client{Timeout: timeout},
		Targets: targets,
		Fall:    fall,
		Rise:    rise,
		fails:   make(map[string]int),
		oks:     make(map[string]int),
	}
}

// CheckOnce probes every target concurrently and applies the results.
func (h *HealthChecker) CheckOnce(ctx context.Context) {
	type result struct {
		node string
		ok   bool
	}
	results := make(chan result, len(h.Targets))
	var wg sync.WaitGroup
	for node, target := range h.Targets {
		wg.Add(1)
		go func(node, target string) {
			defer wg.Done()
			results <- result{node: node, ok: h.probe(ctx, target)}
		}(node, target)
	}
	wg.Wait()
	close(results)
	for res := range results {
		h.apply(res.node, res.ok)
	}
}

func (h *HealthChecker) probe(ctx context.Context, target string) bool {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, target, nil)
	if err != nil {
		return false
	}
	resp, err := h.Client.Do(req)
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	_, _ = io.Copy(io.Discard, resp.Body)
	return resp.StatusCode >= 200 && resp.StatusCode < 300
}

func (h *HealthChecker) apply(node string, ok bool) {
	h.mu.Lock()
	defer h.mu.Unlock()
	healthy := h.Ring.IsHealthy(node)
	if ok {
		h.fails[node] = 0
		h.oks[node]++
		if !healthy && h.oks[node] >= h.Rise {
			h.Ring.SetHealthy(node, true)
			if h.OnChange != nil {
				h.OnChange(node, true)
			}
		}
		return
	}
	h.oks[node] = 0
	h.fails[node]++
	if healthy && h.fails[node] >= h.Fall {
		h.Ring.SetHealthy(node, false)
		if h.OnChange != nil {
			h.OnChange(node, false)
		}
	}
}

// Run checks immediately and then every interval until ctx is cancelled.
func (h *HealthChecker) Run(ctx context.Context, interval time.Duration) {
	h.CheckOnce(ctx)
	ticker := time.NewTicker(interval)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			h.CheckOnce(ctx)
		}
	}
}

// ---------------------------------------------------------------------------
// Reverse proxy router
// ---------------------------------------------------------------------------

// Router proxies each request to the ring owner of its session key.
type Router struct {
	Ring    *Ring
	KeyFunc func(*http.Request) string
	proxies map[string]*httputil.ReverseProxy
}

// SessionKey uses X-User-ID for stickiness, falling back to client IP.
func SessionKey(r *http.Request) string {
	if id := r.Header.Get("X-User-ID"); id != "" {
		return "user:" + id
	}
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		host = r.RemoteAddr
	}
	return "ip:" + host
}

// NewRouter registers backends (node name -> base URL) on the ring.
func NewRouter(ring *Ring, backends map[string]string) (*Router, error) {
	rt := &Router{Ring: ring, KeyFunc: SessionKey, proxies: make(map[string]*httputil.ReverseProxy)}
	for node, raw := range backends {
		u, err := url.Parse(raw)
		if err != nil {
			return nil, fmt.Errorf("backend %s: %w", node, err)
		}
		p := httputil.NewSingleHostReverseProxy(u)
		p.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
			http.Error(w, "bad gateway", http.StatusBadGateway)
		}
		rt.proxies[node] = p
		ring.Add(node)
	}
	return rt, nil
}

func (rt *Router) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	node, ok := rt.Ring.Get(rt.KeyFunc(r))
	if !ok {
		http.Error(w, "no healthy backends", http.StatusServiceUnavailable)
		return
	}
	w.Header().Set("X-Backend", node)
	rt.proxies[node].ServeHTTP(w, r)
}

// ---------------------------------------------------------------------------
// Demo
// ---------------------------------------------------------------------------

type backend struct {
	name string
	up   atomic.Bool
	srv  *httptest.Server
}

func newBackend(name string) *backend {
	b := &backend{name: name}
	b.up.Store(true)
	b.srv = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/healthz" {
			if !b.up.Load() {
				http.Error(w, "draining", http.StatusServiceUnavailable)
				return
			}
			_, _ = io.WriteString(w, "ok")
			return
		}
		fmt.Fprintf(w, "served by %s", name)
	}))
	return b
}

func main() {
	fmt.Println("Step 41 — Consistent-hash sticky load balancer with health checks")

	names := []string{"cache-a", "cache-b", "cache-c"}
	backends := map[string]*backend{}
	urls, health := map[string]string{}, map[string]string{}
	for _, n := range names {
		b := newBackend(n)
		defer b.srv.Close()
		backends[n] = b
		urls[n] = b.srv.URL
		health[n] = b.srv.URL + "/healthz"
	}

	ring := NewRing(160)
	router, err := NewRouter(ring, urls)
	if err != nil {
		panic(err)
	}
	lb := httptest.NewServer(router)
	defer lb.Close()

	checker := NewHealthChecker(ring, health, 2, 2, 500*time.Millisecond)
	checker.OnChange = func(node string, healthy bool) {
		state := "DOWN"
		if healthy {
			state = "UP"
		}
		fmt.Printf("    [health] %s -> %s\n", node, state)
	}

	users := []string{"alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"}
	route := func() map[string]string {
		out := map[string]string{}
		for _, u := range users {
			req, _ := http.NewRequest(http.MethodGet, lb.URL+"/profile", nil)
			req.Header.Set("X-User-ID", u)
			resp, err := http.DefaultClient.Do(req)
			if err != nil {
				out[u] = "error: " + err.Error()
				continue
			}
			body, _ := io.ReadAll(resp.Body)
			resp.Body.Close()
			out[u] = strings.TrimPrefix(string(body), "served by ")
		}
		return out
	}
	show := func(title string, now, before map[string]string) {
		fmt.Println("\n" + title)
		for _, u := range users {
			mark := ""
			if before != nil && before[u] != now[u] {
				mark = "   <- moved"
			}
			fmt.Printf("    %-6s -> %s%s\n", u, now[u], mark)
		}
	}

	ctx := context.Background()
	checker.CheckOnce(ctx)
	initial := route()
	show("[1] Sticky routing: each user pinned to one cache node", initial, nil)

	victim := initial["alice"]
	fmt.Printf("\n[2] %s starts failing health checks (fall=2: one blip is tolerated)\n", victim)
	backends[victim].up.Store(false)
	checker.CheckOnce(ctx)
	fmt.Printf("    after 1 failed probe: %s healthy=%v\n", victim, ring.IsHealthy(victim))
	checker.CheckOnce(ctx)
	failover := route()
	show("    only users of the failed node move; everyone else keeps their warm cache", failover, initial)

	fmt.Printf("\n[3] %s recovers (rise=2) and its users return home\n", victim)
	backends[victim].up.Store(true)
	checker.CheckOnce(ctx)
	checker.CheckOnce(ctx)
	show("    routing restored", route(), failover)

	fmt.Println("\n[4] Capacity change: adding cache-d moves ~1/4 of 10,000 keys (mod-N hashing would move ~3/4)")
	before := map[string]string{}
	for i := range 10000 {
		k := "user:" + strconv.Itoa(i)
		before[k], _ = ring.Get(k)
	}
	ring.Add("cache-d")
	moved := 0
	for k, owner := range before {
		if now, _ := ring.Get(k); now != owner {
			moved++
		}
	}
	fmt.Printf("    keys moved: %d / 10000 (%.1f%%)\n", moved, float64(moved)/100)
	fmt.Printf("    replica set for user:42 (N=3): %v\n", ring.GetN("user:42", 3))
}
