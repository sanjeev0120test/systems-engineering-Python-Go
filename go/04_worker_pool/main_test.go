package main

import (
	"testing"
)

func TestParseLogLine(t *testing.T) {
	line := `127.0.0.1 - - [27/May/2026:10:00:01 +0000] "GET /health HTTP/1.1" 200 12 0.003`
	got, err := ParseLogLine(line)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.Method != "GET" || got.Path != "/health" || got.Status != 200 {
		t.Fatalf("ParseLogLine() = %+v, want GET /health 200", got)
	}
}

func TestParseLogLineInvalid(t *testing.T) {
	if _, err := ParseLogLine("not a log line"); err == nil {
		t.Fatal("expected error for invalid line")
	}
}

func TestProcessLines(t *testing.T) {
	lines := []string{
		`127.0.0.1 - - [27/May/2026:10:00:01 +0000] "GET /health HTTP/1.1" 200 12 0.003`,
		`127.0.0.1 - - [27/May/2026:10:00:02 +0000] "GET /api/users HTTP/1.1" 200 1024 0.045`,
		`127.0.0.1 - - [27/May/2026:10:00:03 +0000] "GET /api/orders HTTP/1.1" 500 128 0.120`,
		`127.0.0.1 - - [27/May/2026:10:00:04 +0000] "POST /api/login HTTP/1.1" 401 64 0.015`,
	}

	counts := ProcessLines(lines, 3)
	want := map[int]int{200: 2, 500: 1, 401: 1}
	for status, wantCount := range want {
		if counts[status] != wantCount {
			t.Fatalf("status %d count = %d, want %d (full map=%v)", status, counts[status], wantCount, counts)
		}
	}
}

func TestProcessLinesEmpty(t *testing.T) {
	counts := ProcessLines(nil, 2)
	if len(counts) != 0 {
		t.Fatalf("expected empty counts, got %v", counts)
	}
}
