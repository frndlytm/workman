package main

import "flag"

// Implements Value interface from "flag" package
type ExampleVar struct {
	Example struct{}
	flag.Value
}

func (e *ExampleVar) String() string {
	// Return the string representation of the Var
}

func (e *ExampleVar) Set(s string) {
	// Parse the os.Arg string into the pointer
}