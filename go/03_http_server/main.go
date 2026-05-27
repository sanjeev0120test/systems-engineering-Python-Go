package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

const DefaultAddr = ":8081"

// HealthResponse is returned by GET /health.
type HealthResponse struct {
	Status string `json:"status"`
}

// HealthHandler writes a JSON health payload.
func HealthHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(HealthResponse{Status: "ok"})
}

// NewMux registers routes for this step.
func NewMux() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", HealthHandler)
	return mux
}

func main() {
	srv := &http.Server{
		Addr:    DefaultAddr,
		Handler: NewMux(),
	}
	fmt.Printf("Step 34 — HTTP server listening on %s (GET /health)\n", DefaultAddr)
	log.Fatal(srv.ListenAndServe())
}
