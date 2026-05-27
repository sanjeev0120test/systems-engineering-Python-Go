package main

import (
	"strings"
	"testing"
)

func TestAdd(t *testing.T) {
	if got := Add(2, 3); got != 5 {
		t.Fatalf("Add(2, 3) = %d, want 5", got)
	}
}

func TestGreet(t *testing.T) {
	got := Greet(User{Name: "alex", Role: "engineer"})
	want := "Hello, alex (engineer)"
	if got != want {
		t.Fatalf("Greet() = %q, want %q", got, want)
	}
}

func TestDivide(t *testing.T) {
	got, err := Divide(10, 4)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != 2.5 {
		t.Fatalf("Divide(10, 4) = %v, want 2.5", got)
	}

	_, err = Divide(1, 0)
	if err == nil {
		t.Fatal("expected divide-by-zero error")
	}
	if !strings.Contains(err.Error(), "divide by zero") {
		t.Fatalf("unexpected error: %v", err)
	}
}
