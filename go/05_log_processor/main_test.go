package main

import (
	"os"
	"path/filepath"
	"testing"
)

func sampleLogPath(t *testing.T) string {
	t.Helper()
	path := filepath.Join("..", "..", "sample_data", "logs", "access.log")
	if _, err := os.Stat(path); err != nil {
		t.Fatalf("sample log missing at %s: %v", path, err)
	}
	return path
}

func TestParseLine(t *testing.T) {
	method, status, err := ParseLine(`127.0.0.1 - - [27/May/2026:10:00:07 +0000] "GET /api/orders HTTP/1.1" 503 96 0.250`)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if method != "GET" || status != 503 {
		t.Fatalf("ParseLine() = (%q, %d), want (GET, 503)", method, status)
	}
}

func TestParseAccessLog(t *testing.T) {
	summary, err := ParseAccessLog(sampleLogPath(t), 4)
	if err != nil {
		t.Fatalf("ParseAccessLog() error: %v", err)
	}

	if summary.TotalLines != 8 {
		t.Fatalf("TotalLines = %d, want 8", summary.TotalLines)
	}
	if summary.ErrorLines != 3 {
		t.Fatalf("ErrorLines = %d, want 3", summary.ErrorLines)
	}

	wantStatus := map[int]int{200: 5, 401: 1, 500: 1, 503: 1}
	for status, wantCount := range wantStatus {
		if summary.StatusCounts[status] != wantCount {
			t.Fatalf("status %d count = %d, want %d", status, summary.StatusCounts[status], wantCount)
		}
	}

	if summary.MethodCounts["GET"] != 7 {
		t.Fatalf("GET count = %d, want 7", summary.MethodCounts["GET"])
	}
	if summary.MethodCounts["POST"] != 1 {
		t.Fatalf("POST count = %d, want 1", summary.MethodCounts["POST"])
	}
}

func TestParseAccessLogMissingFile(t *testing.T) {
	_, err := ParseAccessLog("does-not-exist.log", 2)
	if err == nil {
		t.Fatal("expected error for missing file")
	}
}
