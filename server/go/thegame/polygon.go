package main

import (
	"fmt"

	"github.com/afg984/thegame/server/go/thegame/pb"
)

type Shape int

const (
	Square   Shape = 4
	Triangle Shape = 3
	Pentagon Shape = 5
)

type Polygon struct {
	Entity
	id    int
	shape Shape
}

func (p *Polygon) ID() int {
	return p.id
}

func (p *Polygon) String() string {
	return fmt.Sprintf("%s#%d", p.ShapeString(), p.id)
}

func (p *Polygon) ShapeString() string {
	switch p.shape {
	case Square:
		return "Square"
	case Triangle:
		return "Triangle"
	case Pentagon:
		return "Pentagon"
	default:
		return "Polygon?"
	}
}

func (p *Polygon) ToProto() *pb.Polygon {
	return &pb.Polygon{
		Entity: EntityToProto(p),
		Edges:  int32(p.Edges()),
	}
}

func (p *Polygon) MaxHealth() int {
	switch p.shape {
	case Square:
		return 100
	case Triangle:
		return 300
	case Pentagon:
		return 1000
	default:
		panic("Unknown shape")
	}
}

func (p *Polygon) Edges() int {
	return int(p.shape)
}

func (p *Polygon) Friction() float64 {
	return 0.04
}

func (p *Polygon) IsBounded() bool {
	return true
}

func (p *Polygon) MaxSpeed() float64 {
	return 5
}

func (p *Polygon) Radius() float64 {
	switch p.shape {
	case Square:
		return 20
	case Triangle:
		return 20
	case Pentagon:
		return 25
	default:
		panic("Unknown shape")
	}
}

func (p *Polygon) Team() int {
	return 0
}

func (p *Polygon) BodyDamage() int {
	switch p.shape {
	case Square:
		return 10
	case Triangle:
		return 20
	case Pentagon:
		return 40
	default:
		panic("Unknown shape")
	}
}

func (p *Polygon) CanAcquireExperience() bool {
	return false
}

func (p *Polygon) AcquireExperience(int) {
}

func (p *Polygon) RewardingExperience() int {
	switch p.shape {
	case Square:
		return 10
	case Triangle:
		return 60
	case Pentagon:
		return 360
	default:
		panic("Unknown shape")
	}
}
