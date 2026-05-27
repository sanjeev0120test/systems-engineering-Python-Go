package main

import (
	"reflect"
	"testing"
)

func TestSquare(t *testing.T) {
	if got := Square(7); got != 49 {
		t.Fatalf("Square(7) = %d, want 49", got)
	}
}

func TestSumConcurrent(t *testing.T) {
	nums := []int{1, 2, 3, 4, 5}
	if got := SumConcurrent(nums); got != 15 {
		t.Fatalf("SumConcurrent() = %d, want 15", got)
	}
	if got := SumConcurrent(nil); got != 0 {
		t.Fatalf("SumConcurrent(nil) = %d, want 0", got)
	}
}

func TestSquareAll(t *testing.T) {
	nums := []int{1, 2, 3, 4}
	want := []int{1, 4, 9, 16}
	if got := SquareAll(nums); !reflect.DeepEqual(got, want) {
		t.Fatalf("SquareAll() = %v, want %v", got, want)
	}
}
