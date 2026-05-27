package main

import (
	"fmt"
	"os"
)

// User represents a platform operator (struct demo).
type User struct {
	Name string
	Role string
}

// Add demonstrates basic types and functions.
func Add(a, b int) int {
	return a + b
}

// Greet formats a greeting from a struct value.
func Greet(u User) string {
	return fmt.Sprintf("Hello, %s (%s)", u.Name, u.Role)
}

// Divide returns a/b or an error when b is zero.
func Divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, fmt.Errorf("divide by zero")
	}
	return a / b, nil
}

func main() {
	fmt.Println("Step 32 — Go basics")
	fmt.Printf("Add(2, 3) = %d\n", Add(2, 3))

	u := User{Name: "sre", Role: "oncall"}
	fmt.Println(Greet(u))

	result, err := Divide(10, 4)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Printf("Divide(10, 4) = %.2f\n", result)

	if _, err := Divide(1, 0); err != nil {
		fmt.Printf("Expected error: %v\n", err)
	}
}
