package main

type GameCommand int

const (
	CommandPause GameCommand = iota
	CommandResume
	CommandTick
	CommandReset
)
