package main

import (
	"time"
)

const tickTime = time.Millisecond * 33

type Arena struct {
	tickCount int64
	debris    []*Debris
	heroes    []*Hero
}

func NewArena() *Arena {
	a := &Arena{
		tickCount: 0,
	}
	for i := 0; i < 10; i++ {
		a.debris[i].dtype = Pentagon
	}
	for i := 10; i < 60; i++ {
		a.debris[i].dtype = Triangle
	}
	for i := 60; i < 300; i++ {
		a.debris[i].dtype = Pentagon
	}
	return a
}

func (a *Arena) tick() {
	a.tickCount++
	var objects []Collidable
	for _, d := range a.debris {
		d.tick()
		objects = append(objects, d)
	}
	for _, h := range a.heroes {
		objects = append(objects, h)
	}
	DoCollision(objects)
}

func (a *Arena) Run() {
	for _ = range time.Tick(tickTime) {
		a.tick()
	}
}
