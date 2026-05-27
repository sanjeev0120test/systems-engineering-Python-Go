package main

import (
	"fmt"
	"strconv"
	"strings"
	"sync"
)

// LogLine holds parsed fields from one access-log line.
type LogLine struct {
	Method string
	Path   string
	Status int
}

// ParseLogLine parses a single nginx-style access log line.
func ParseLogLine(line string) (LogLine, error) {
	line = strings.TrimSpace(line)
	if line == "" {
		return LogLine{}, fmt.Errorf("empty line")
	}

	parts := strings.Split(line, `"`)
	if len(parts) < 3 {
		return LogLine{}, fmt.Errorf("invalid log line")
	}

	reqFields := strings.Fields(parts[1])
	if len(reqFields) < 2 {
		return LogLine{}, fmt.Errorf("invalid request segment")
	}

	tail := strings.Fields(strings.TrimSpace(parts[2]))
	if len(tail) < 1 {
		return LogLine{}, fmt.Errorf("missing status code")
	}

	status, err := strconv.Atoi(tail[0])
	if err != nil {
		return LogLine{}, fmt.Errorf("invalid status: %w", err)
	}

	return LogLine{
		Method: reqFields[0],
		Path:   reqFields[1],
		Status: status,
	}, nil
}

// ProcessLines counts HTTP status codes using a worker pool.
func ProcessLines(lines []string, workers int) map[int]int {
	if workers < 1 {
		workers = 1
	}

	jobs := make(chan string)
	results := make(chan int)

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for line := range jobs {
				entry, err := ParseLogLine(line)
				if err != nil {
					continue
				}
				results <- entry.Status
			}
		}()
	}

	go func() {
		for _, line := range lines {
			jobs <- line
		}
		close(jobs)
		wg.Wait()
		close(results)
	}()

	counts := make(map[int]int)
	for status := range results {
		counts[status]++
	}
	return counts
}

func main() {
	sample := []string{
		`127.0.0.1 - - [27/May/2026:10:00:01 +0000] "GET /health HTTP/1.1" 200 12 0.003`,
		`127.0.0.1 - - [27/May/2026:10:00:03 +0000] "GET /api/orders HTTP/1.1" 500 128 0.120`,
		`127.0.0.1 - - [27/May/2026:10:00:04 +0000] "POST /api/login HTTP/1.1" 401 64 0.015`,
	}

	counts := ProcessLines(sample, 2)
	fmt.Println("Step 35 — Worker pool status counts:")
	for status, count := range counts {
		fmt.Printf("  %d -> %d\n", status, count)
	}
}
