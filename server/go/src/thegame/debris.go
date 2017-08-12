package main

import (
	"thegame/pb"
)

const (
	_        = iota
	Square   = iota
	Triangle = iota
	Pentagon = iota
)

type Debris struct {
	Entity
	dtype int
}

func (d *Debris) ToProto() *pb.Debris {
	return &pb.Debris{
		Entity: d.Entity.ToProto(),
		Radius: d.Radius(),
	}
}

func (d *Debris) Friction() float64 {
	return 0.04
}

func (d *Debris) IsBounded() bool {
	return true
}

func (d *Debris) MaxSpeed() float64 {
	return 5
}

func (d *Debris) Radius() float64 {
	switch d.dtype {
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

func (d *Debris) Team() int {
	return 0
}

func (d *Debris) BodyDamage() int {
	switch d.dtype {
	case Square:
		return 10
	case Triangle:
		return 15
	case Pentagon:
		return 25
	default:
		panic("Unknown shape")
	}
}

func (d *Debris) AcquireExperience(int) {
	return
}

func (d *Debris) RewardingExperience() int {
	switch d.dtype {
	case Square:
		return 10
	case Triangle:
		return 30
	case Pentagon:
		return 250
	default:
		panic("Unknown shape")
	}
}
