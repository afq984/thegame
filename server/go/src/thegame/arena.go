package main

import (
	"container/list"
	"log"
	"thegame/pb"
	"time"
)

const tickTime = time.Millisecond * 33

type HeroControls struct {
	*Hero
	*pb.Controls
}

type Arena struct {
	tickCount   int64
	debris      [300]*Debris
	heroCounter int
	heroes      *list.List
	bullets     []*Bullet
	controlChan chan HeroControls
	joinChan    chan chan *list.Element
	quitChan    chan *list.Element
}

func NewArena() *Arena {
	a := &Arena{
		tickCount: 0,
		heroes:    list.New(),
	}
	for i := 0; i < 10; i++ {
		a.debris[i] = &Debris{dtype: Pentagon}
	}
	for i := 10; i < 60; i++ {
		a.debris[i] = &Debris{dtype: Triangle}
	}
	for i := 60; i < 300; i++ {
		a.debris[i] = &Debris{dtype: Square}
	}
	return a
}

func (a *Arena) Join() *list.Element {
	c := make(chan *list.Element)
	a.joinChan <- c
	return <-c
}

func (a *Arena) tick() {
	a.tickCount++
	var objects []Collidable
	for _, d := range a.debris {
		TickPosition(d)
		objects = append(objects, d)
	}
	for e := a.heroes.Front(); e != nil; e = e.Next() {
		h := e.Value.(*Hero)
		TickPosition(h)
		objects = append(objects, h)
	}
	for _, b := range a.bullets {
		TickPosition(b)
		objects = append(objects, b)
	}

	DoCollision(objects)

	for _, b := range a.bullets {
		b.timeout--
	}
	filterBullets(a.bullets)

	for e := a.heroes.Front(); e != nil; e = e.Next() {
		h := e.Value.(*Hero)
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
	for {
		select {
		case <-time.Tick(tickTime):
			a.tick()
		case hc := <-a.controlChan:
			hc.Hero.controls = hc.Controls
		case jc := <-a.joinChan:
			a.heroCounter++
			h := NewHero(a.heroCounter)
			log.Printf("New hero #%d", a.heroCounter)
			jc <- a.heroes.PushBack(h)
		case l := <-a.quitChan:
			a.heroes.Remove(l)
		}
	}
}
