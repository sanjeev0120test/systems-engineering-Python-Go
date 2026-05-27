package main

import (
	"fmt"
	"sync"
)

// Square returns n squared.
func Square(n int) int {
	return n * n
}

// SumConcurrent adds integers using goroutines and a mutex (like synchronized in Java).
func SumConcurrent(nums []int) int {
	if len(nums) == 0 {
		return 0
	}

	var mu sync.Mutex
	total := 0
	var wg sync.WaitGroup

	for _, n := range nums {
		wg.Add(1)
		go func(v int) {
			defer wg.Done()
			mu.Lock()
			total += v
			mu.Unlock()
		}(n)
	}

	wg.Wait()
	return total
}

// SquareAll returns squares computed concurrently, preserving order.
func SquareAll(nums []int) []int {
	if len(nums) == 0 {
		return nil
	}

	out := make([]int, len(nums))
	ch := make(chan struct {
		index int
		value int
	}, len(nums))

	var wg sync.WaitGroup
	for i, n := range nums {
		wg.Add(1)
		go func(idx, val int) {
			defer wg.Done()
			ch <- struct {
				index int
				value int
			}{idx, Square(val)}
		}(i, n)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	for result := range ch {
		out[result.index] = result.value
	}
	return out
}

func main() {
	fmt.Println("Step 33 — Go concurrency")
	nums := []int{1, 2, 3, 4, 5}
	fmt.Printf("SumConcurrent(%v) = %d\n", nums, SumConcurrent(nums))
	fmt.Printf("SquareAll(%v) = %v\n", nums, SquareAll(nums))
}
