package main

var flagvar int

func init() {
	flag.IntVar(
        &flagvar,
        "flagname",
        1234,
        "help message for flagname"
    )
}