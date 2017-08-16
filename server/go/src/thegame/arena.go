package main

import (
	"container/list"
	"flag"
	"log"
	"math/rand"
	"sort"
	"time"

	"thegame/pb"
)

var ticksPerSecond int

func init() {
	flag.IntVar(&ticksPerSecond, "tps", 30, "ticks per second")
}

type HeroControls struct {
	*Hero
	*pb.Controls
}

type joinRequest struct {
	name string
	ch   chan *list.Element
}

type Arena struct {
	polygons       [360]*Polygon
	heroCounter    int
	bulletCounter  int
	polygonCounter int
	heroes         *list.List
	bullets        []*Bullet
	controlChan    chan HeroControls
	joinChan       chan joinRequest
	quitChan       chan *list.Element
	commandChan    chan GameCommand
}

func NewArena() *Arena {
	a := &Arena{
		heroes:      list.New(),
		controlChan: make(chan HeroControls),
		joinChan:    make(chan joinRequest),
		quitChan:    make(chan *list.Element),
		commandChan: make(chan GameCommand),
	}
	for i := 0; i < 30; i++ {
		a.polygons[i] = &Polygon{shape: Pentagon}
	}
	for i := 30; i < 90; i++ {
		a.polygons[i] = &Polygon{shape: Triangle}
	}
	for i := 90; i < 360; i++ {
		a.polygons[i] = &Polygon{shape: Square}
	}
	go a.Run()
	return a
}

func (a *Arena) Join(name string) *list.Element {
	c := make(chan *list.Element)
	a.joinChan <- joinRequest{name, c}
	return <-c
}

func (a *Arena) Quit(e *list.Element) {
	a.quitChan <- e
}

func (a *Arena) tick() {
	var objects []Collidable
	for _, p := range a.polygons {
		TickPosition(p)
		if p.visible {
			objects = append(objects, p)
		}
	}
	for e := a.heroes.Front(); e != nil; e = e.Next() {
		h := e.Value.(*Hero)
		if !h.visible {
			h.Spawn()
		}
		TickPosition(h)
		objects = append(objects, h)
	}
	for _, b := range a.bullets {
		TickPosition(b)
		if b.visible {
			objects = append(objects, b)
		}
	}

	DoCollision(objects)

	for _, b := range a.bullets {
		b.timeout--
	}
	a.bullets = filterBullets(a.bullets)

	for e := a.heroes.Front(); e != nil; e = e.Next() {
		h := e.Value.(*Hero)
		h.Action(a)
	}

	// random respawn polygon
	for _, p := range a.polygons {
		if !p.visible {
			if rand.Float64() < 0.008 {
				a.polygonCounter++
				p.id = a.polygonCounter
				p.visible = true
				p.health = p.MaxHealth()
				p.position = RandomPosition()
			}
		}
	}
}

// remove dead and timed out bullets
func filterBullets(a []*Bullet) []*Bullet {
	// https://github.com/golang/go/wiki/SliceTricks#filtering-without-allocating
	b := a[:0]
	for _, x := range a {
		if x.health > 0 && x.timeout > 0 {
			b = append(b, x)
		}
	}
	return b
}

const fieldOfView = 800

func (a *Arena) broadcast() {
	var polygons []*pb.Polygon
	var bullets []*pb.Bullet
	var heroes []*pb.Hero
	var scores []*pb.ScoreEntry
	for _, p := range a.polygons {
		if p.visible {
			polygons = append(polygons, p.ToProto())
		}
	}
	for _, b := range a.bullets {
		bullets = append(bullets, b.ToProto())
	}
	for e := a.heroes.Front(); e != nil; e = e.Next() {
		h := e.Value.(*Hero)
		heroes = append(heroes, h.ToProto())
		scores = append(scores, h.ToScoreEntry())
	}
	sort.Sort(ByScore(scores))
	// send updates to clients
	for e := a.heroes.Front(); e != nil; e = e.Next() {
		h := e.Value.(*Hero)
		canSee := func(w *pb.Entity) bool {
			x := real(h.position)
			y := imag(h.position)
			return (w.Position.X+w.Radius > x-fieldOfView &&
				w.Position.X-w.Radius < x+fieldOfView &&
				w.Position.Y-w.Radius > y-fieldOfView &&
				w.Position.Y-w.Radius < y+fieldOfView)
		}
		var spolygons []*pb.Polygon
		var sbullets []*pb.Bullet
		var sheroes []*pb.Hero
		for _, p := range polygons {
			if canSee(p.Entity) {
				spolygons = append(spolygons, p)
			}
		}
		for _, b := range bullets {
			if canSee(b.Entity) {
				sbullets = append(sbullets, b)
			}
		}
		for _, oh := range heroes {
			if canSee(oh.Entity) {
				sheroes = append(sheroes, oh)
			}
		}
		state := &pb.GameState{
			Meta: &pb.GameState_Meta{
				HeroId: int32(h.id),
				Scores: scores,
			},
			Polygons: spolygons,
			Bullets:  sbullets,
			Heroes:   sheroes,
		}
		select {
		case h.UpdateChan <- state:
		default:
			log.Println(h, "not responding to updates")
		}
	}
}

func (a *Arena) Run() {
	tick := time.Tick(time.Second / time.Duration(ticksPerSecond))
	perfTick := time.Tick(time.Second)
	var tickCount int64
	var lastTick int64
	paused := false
	for {
		select {
		case <-tick:
			if !paused {
				tickCount++
				a.tick()
			}
			a.broadcast()
		case <-perfTick:
			log.Println("ticks per second:", tickCount-lastTick)
			lastTick = tickCount
		case hc := <-a.controlChan:
			hc.Hero.controls = hc.Controls
		case jr := <-a.joinChan:
			a.heroCounter++
			h := NewHero(a.heroCounter, jr.name)
			log.Println(h, "joined the arena")
			jr.ch <- a.heroes.PushBack(h)
		case l := <-a.quitChan:
			log.Println(l.Value.(*Hero), "left the arena")
			a.heroes.Remove(l)
		case c := <-a.commandChan:
			switch c {
			case Pause:
				log.Println("Game Paused")
				paused = true
			case Resume:
				log.Println("Game Resumed")
				paused = false
			case c:
				log.Printf("No known action to %q", c)
			}
		}
	}
}
