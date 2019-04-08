package main

import (
	"math"
	"math/cmplx"
	"math/rand"
)

// Environmental constants
const (
	XMin = 0
	XMax = 5000
	YMin = 0
	YMax = 4000
)

type Movable interface {
	// These methods are defined on type Entity
	Position() complex128
	SetPosition(complex128)
	Velocity() complex128
	SetVelocity(complex128)

	// implement these methods on the concrete types
	Friction() float64
	IsBounded() bool
	MaxSpeed() float64
}

func ApplyFriction(m Movable) {
	// e stands for entity here
	r, phi := cmplx.Polar(m.Velocity())
	r = math.Max(0, r-m.Friction())
	m.SetVelocity(cmplx.Rect(r, phi))
}

func BoundAndBounce(m Movable) {
	px := real(m.Position())
	py := imag(m.Position())
	if px < XMin {
		m.SetVelocity(-cmplx.Conj(m.Velocity()))
		px = XMin
	} else if px > XMax {
		m.SetVelocity(-cmplx.Conj(m.Velocity()))
		px = XMax
	}
	if py < YMin {
		m.SetVelocity(cmplx.Conj(m.Velocity()))
		py = YMin
	} else if py > YMax {
		m.SetVelocity(cmplx.Conj(m.Velocity()))
		py = YMax
	}
	m.SetPosition(complex(px, py))
}

func TickPosition(m Movable) {
	r, phi := cmplx.Polar(m.Velocity())
	r = math.Min(r, m.MaxSpeed())
	m.SetVelocity(cmplx.Rect(r, phi))
	m.SetPosition(m.Position() + m.Velocity())
	if m.IsBounded() {
		BoundAndBounce(m)
	}
	ApplyFriction(m)
}

func randWithin(r *rand.Rand, a, b float64) float64 {
	return r.Float64()*(b-a) + a
}

// RandomPosition returns a random point that is within the arena's bounds
func (a *Arena) RandomPosition() complex128 {
	return complex(randWithin(a.rand, XMin, XMax), randWithin(a.rand, YMin, YMax))
}
