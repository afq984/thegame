package main

import (
	"time"
)

const tickTime = time.Millisecond * 33

type Arena struct {
	tickCount int64
	debris    []*Debris
	heroes    []*Hero
	bullets   []*Bullet
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
		TickPosition(d)
		objects = append(objects, d)
	}
	for _, h := range a.heroes {
		TickPosition(h)
		objects = append(objects, h)
	}
	for _, b := range a.bullets {
		TickPosition(b)
		objects = append(objects, b)
	}
	DoCollision(objects)

	filterBullets(a.bullets)

	for _, h := range a.heroes {
		h.Action(a)
	}
}

// remove dead and timed out bullets
func filterBullets(a []*Bullet) {
	// https://github.com/golang/go/wiki/SliceTricks#filtering-without-allocating
	b := a[:0]
	for _, x := range a {
		if x.health > 0 && x.timeout > 0 {
			b = append(b, x)
		}
	}
}

func (a *Arena) Run() {
	for _ = range time.Tick(tickTime) {
		a.tick()
	}
}
