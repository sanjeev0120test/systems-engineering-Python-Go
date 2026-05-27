package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
	"sync"
)

// Summary aggregates parsed access-log statistics.
type Summary struct {
	TotalLines   int
	StatusCounts map[int]int
	MethodCounts map[string]int
	ErrorLines   int
}

// ParseLine extracts method and status from one access-log line.
func ParseLine(line string) (method string, status int, err error) {
	line = strings.TrimSpace(line)
	if line == "" {
		return "", 0, fmt.Errorf("empty line")
	}

	parts := strings.Split(line, `"`)
	if len(parts) < 3 {
		return "", 0, fmt.Errorf("invalid log line")
	}

	reqFields := strings.Fields(parts[1])
	if len(reqFields) < 1 {
		return "", 0, fmt.Errorf("invalid request segment")
	}

	tail := strings.Fields(strings.TrimSpace(parts[2]))
	if len(tail) < 1 {
		return "", 0, fmt.Errorf("missing status code")
	}

	code, convErr := strconv.Atoi(tail[0])
	if convErr != nil {
		return "", 0, fmt.Errorf("invalid status: %w", convErr)
	}

	return reqFields[0], code, nil
}

// ParseAccessLog reads a log file and aggregates stats with a worker pool.
func ParseAccessLog(path string, workers int) (Summary, error) {
	file, err := os.Open(path)
	if err != nil {
		return Summary{}, err
	}
	defer file.Close()

	if workers < 1 {
		workers = 1
	}

	type parsed struct {
		method string
		status int
	}

	jobs := make(chan string)
	results := make(chan parsed)

	var wg sync.WaitGroup
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for line := range jobs {
				method, status, err := ParseLine(line)
				if err != nil {
					continue
				}
				results <- parsed{method: method, status: status}
			}
		}()
	}

	go func() {
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			jobs <- scanner.Text()
		}
		close(jobs)
		wg.Wait()
		close(results)
	}()

	summary := Summary{
		StatusCounts: make(map[int]int),
		MethodCounts: make(map[string]int),
	}

	for entry := range results {
		summary.TotalLines++
		summary.StatusCounts[entry.status]++
		summary.MethodCounts[entry.method]++
		if entry.status >= 400 {
			summary.ErrorLines++
		}
	}

	if err := file.Err(); err != nil {
		return Summary{}, err
	}

	return summary, nil
}

func main() {
	path := "../../sample_data/logs/access.log"
	summary, err := ParseAccessLog(path, 4)
	if err != nil {
		fmt.Fprintf(os.Stderr, "parse failed: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Step 36 — Log processor summary")
	fmt.Printf("  total lines: %d\n", summary.TotalLines)
	fmt.Printf("  error lines (4xx/5xx): %d\n", summary.ErrorLines)
	fmt.Println("  status counts:")
	for status, count := range summary.StatusCounts {
		fmt.Printf("    %d -> %d\n", status, count)
	}
}
