package main

import (
	"container/list"
	"flag"
	"fmt"
	"log"
	"math/rand"
	"sort"
	"sync"
	"time"

	"github.com/afg984/thegame/server/go/thegame/pb"
)

var ticksPerSecond int
var startGameAsPaused bool
var mustSendUpdates bool

func init() {
	flag.IntVar(&ticksPerSecond, "tps", 30, "ticks per second")
	flag.BoolVar(&startGameAsPaused, "pause", false, "start game as paused")
	flag.BoolVar(&mustSendUpdates, "must-send-updates", false, "don't allow dropping game updates")
}

type HeroControls struct {
	*Hero
	*pb.Controls
}

type joinRequest struct {
	name string
	ch   chan *list.Element
}

type commandAndResponse struct {
	command GameCommand
	done    chan bool
}

type Arena struct {
	rand                *rand.Rand
	polygons            [360]*Polygon
	heroCounter         int
	bulletCounter       int
	polygonCounter      int
	heroes              *list.List
	bullets             []*Bullet
	controlChan         chan HeroControls
	joinChan            chan joinRequest
	quitChan            chan *list.Element
	commandChan         chan commandAndResponse
	viewRemotes         []chan *pb.GameState
	viewChan            chan chan *pb.GameState
	waitForControlsChan chan struct{}
	waitForControlsLock sync.Mutex
	nControlsReceived   int
}

func NewArena() *Arena {
	a := &Arena{
		rand:                rand.New(rand.NewSource(1)),
		heroes:              list.New(),
		controlChan:         make(chan HeroControls),
		joinChan:            make(chan joinRequest),
		quitChan:            make(chan *list.Element),
		commandChan:         make(chan commandAndResponse),
		viewChan:            make(chan chan *pb.GameState),
		waitForControlsChan: make(chan struct{}),
	}
	a.reset()
	go a.Run()
	return a
}

type HeroHandle struct {
	element *list.Element
	hero    *Hero
}

func newHeroHandle(element *list.Element) *HeroHandle {
	return &HeroHandle{
		element: element,
		hero:    element.Value.(*Hero),
	}
}

func (hh *HeroHandle) UpdateChan() chan *pb.GameState {
	return hh.hero.UpdateChan
}

func (hh *HeroHandle) HeroControls(controls *pb.Controls) HeroControls {
	return HeroControls{
		hh.hero,
		controls,
	}
}

func (hh *HeroHandle) String() string {
	return fmt.Sprintf("HeroHandle#%d", hh.hero.id)
}

func (a *Arena) reset() {
	for e := a.heroes.Front(); e != nil; e = e.Next() {
		h := e.Value.(*Hero)
		h.score = 0
		h.ReadyToSpawn()
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
}

func (a *Arena) Join(name string) *HeroHandle {
	c := make(chan *list.Element)
	a.joinChan <- joinRequest{name, c}
	return newHeroHandle(<-c)
}

func (a *Arena) Quit(hh *HeroHandle) {
	a.quitChan <- hh.element
}

// gc cleans up unused objects
func (a *Arena) gc() {
	// remove disconnected and dead heroes
	var next *list.Element
	for e := a.heroes.Front(); e != nil; e = next {
		next = e.Next()

		h := e.Value.(*Hero)
		if h.health <= 0 && h.disconnected {
			a.heroes.Remove(e)
		}
	}
}

func (a *Arena) tick() {
	a.gc()

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
			h.TryRespawn(a)
		}
		if h.visible {
			TickPosition(h)
			objects = append(objects, h)
		}
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
		if h.visible && !h.disconnected {
			h.Action(a)
		}
		h.controls = nil
	}

	// random respawn polygon
	for _, p := range a.polygons {
		if !p.visible {
			if a.rand.Float64() < 0.008 {
				a.polygonCounter++
				p.id = a.polygonCounter
				p.visible = true
				p.health = p.MaxHealth()
				p.position = a.RandomPosition()
			}
		}
	}

	a.waitForControlsLock.Lock()
	select {
	case <-a.waitForControlsChan:
	default:
		close(a.waitForControlsChan)
	}
	a.waitForControlsChan = make(chan struct{})
	a.waitForControlsLock.Unlock()
	a.nControlsReceived = 0
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

func (a *Arena) broadcastView(gs *pb.GameState) {
	remotes := a.viewRemotes[:0]
	for _, remote := range a.viewRemotes {
		select {
		case remote <- gs:
			remotes = append(remotes, remote)
		default:
			close(remote)
			log.Println("view client not responding to updates")
		}
	}
	a.viewRemotes = remotes
}

func (a *Arena) broadcast() {
	var polygons []*pb.Polygon
	var bullets []*pb.Bullet
	var heroes []*pb.Hero
	var scores []*pb.ScoreEntry
	maxScore := 0
	var maxScoreHero *Hero
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
		if h.visible {
			if h.score > maxScore && !h.disconnected {
				maxScore = h.score
				maxScoreHero = h
			}
			heroes = append(heroes, h.ToProto())
		}
		scores = append(scores, h.ToScoreEntry())
	}
	sort.Sort(ByScore(scores))
	// send updates to clients
	for e := a.heroes.Front(); e != nil; e = e.Next() {
		h := e.Value.(*Hero)
		if h.disconnected {
			continue
		}
		focusHero := h
		if !h.visible {
			switch lastHit := focusHero.lastHit.(type) {
			case *Hero:
				focusHero = lastHit
			case *Bullet:
				focusHero = lastHit.owner
			default:
				focusHero = h
			}
		}
		x := real(focusHero.position)
		y := imag(focusHero.position)
		canSee := func(w *pb.Entity) bool {
			return (w.Position.X+w.Radius > x-fieldOfView &&
				w.Position.X-w.Radius < x+fieldOfView &&
				w.Position.Y-w.Radius > y-fieldOfView &&
				w.Position.Y-w.Radius < y+fieldOfView)
		}
		var spolygons []*pb.Polygon
		var sbullets []*pb.Bullet
		sheroes := []*pb.Hero{h.ToProto()}
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
			if oh.Entity.Id == int32(h.id) {
				continue
			}
			if canSee(oh.Entity) {
				sheroes = append(sheroes, oh)
			}
		}
		state := &pb.GameState{
			Meta: &pb.GameState_Meta{
				HeroId:         int32(h.id),
				Scores:         scores,
				CenterPosition: &pb.Vector{X: x, Y: y},
			},
			Polygons: spolygons,
			Bullets:  sbullets,
			Heroes:   sheroes,
		}
		if mustSendUpdates {
			h.UpdateChan <- state
		} else {
			select {
			case h.UpdateChan <- state:
			default:
				log.Println(h, "not responding to updates")
			}
		}
		if h == maxScoreHero {
			a.broadcastView(state)
		}
	}
}

func (a *Arena) Run() {
	tick := time.Tick(time.Second / time.Duration(ticksPerSecond))
	perfTick := time.Tick(time.Second)
	var tickCount int64
	var lastTick int64
	paused := startGameAsPaused
	for {
		select {
		case <-tick:
			if !paused {
				tickCount++
				a.tick()
			}
			if !mustSendUpdates || !paused {
				a.broadcast()
			}
		case <-perfTick:
			if !paused {
				log.Println("ticks per second:", tickCount-lastTick)
			}
			lastTick = tickCount
		case hc := <-a.controlChan:
			if hc.Hero.controls == nil {
				a.nControlsReceived++
				// XXX
				// Since the number of heroes can change between ticks,
				// this sometimes causes problems as closing an already
				// closed channel panics.
				// A check would work, but maybe a more robust method to
				// check controls should be implemented, or, only allow
				// joins and leaves in ticks.
				if a.nControlsReceived >= a.heroes.Len() {
					close(a.waitForControlsChan)
				}
			}
			hc.Hero.controls = hc.Controls
		case jr := <-a.joinChan:
			a.heroCounter++
			h := NewHero(a.heroCounter, jr.name)
			h.ReadyToSpawn()
			log.Println(h, "joined the arena")
			jr.ch <- a.heroes.PushBack(h)
		case l := <-a.quitChan:
			h := l.Value.(*Hero)
			log.Println(h, "left the arena")
			h.disconnected = true
		case cgs := <-a.viewChan:
			a.viewRemotes = append(a.viewRemotes, cgs)
		case c := <-a.commandChan:
			switch c.command {
			case CommandPause:
				paused = true
				log.Println("Game Paused")
			case CommandResume:
				paused = false
				log.Println("Game Resumed")
			case CommandTick:
				tickCount++
				a.tick()
				a.broadcast()
			case CommandReset:
				log.Println("Game Reset")
				a.reset()
			default:
				log.Printf("No known action to %q", c.command)
			}
			c.done <- true
		}
	}
}

func (a *Arena) Command(cmd GameCommand) chan bool {
	c := commandAndResponse{
		cmd,
		make(chan bool, 1),
	}
	a.commandChan <- c
	return c.done
}

// AllControlsReceived returns a channel that will be closed
// after all the heroes have sent their controls.
// This is EXPERIMENTAL.
func (a *Arena) AllControlsReceived() chan struct{} {
	a.waitForControlsLock.Lock()
	ch := a.waitForControlsChan
	a.waitForControlsLock.Unlock()
	return ch
}

// Seeds the arena's RNG
func (a *Arena) Seed(seed int64) {
	a.rand.Seed(seed)
}
