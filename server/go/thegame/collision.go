package main

import (
	"math/cmplx"
	"sort"
)

type Collidable interface {
	// these methods are defined on type Entity
	Position() complex128
	Velocity() complex128
	SetVelocity(complex128)
	Visible() bool
	SetVisible(bool)
	Health() int
	SetHealth(int)
	LastHit() Collidable
	SetLastHit(Collidable)

	// implement these methods on the concrete types
	Radius() float64
	Team() int // Objects in the same Team() will not do damage with each other
	BodyDamage() int
	CanAcquireExperience() bool // whether the entity can get experience by killing others
	AcquireExperience(int)
	RewardingExperience() int
}

func Collide(a, b Collidable) {
	dist, phi := cmplx.Polar(a.Position() - b.Position())
	rsum := a.Radius() + b.Radius()
	if dist > rsum {
		return
	}
	a.SetVelocity(a.Velocity() + cmplx.Rect((rsum-dist)/rsum+0.1, phi))
	b.SetVelocity(b.Velocity() + cmplx.Rect((dist-rsum)/rsum+0.1, phi))
	if a.Team() != b.Team() {
		Hit(a, b)
		Hit(b, a)
	}
}

func Hit(a, b Collidable) {
	hp := b.Health()
	hp -= a.BodyDamage()
	b.SetHealth(hp)
	if a.CanAcquireExperience() {
		b.SetLastHit(a)
	}
	if hp <= 0 {
		b.SetVisible(false)
		if b.LastHit() != nil {
			b.LastHit().AcquireExperience(b.RewardingExperience())
		}
	}
}

func leftBound(c Collidable) float64 {
	return real(c.Position()) - c.Radius()
}

func rightBound(c Collidable) float64 {
	return real(c.Position()) + c.Radius()
}

func topBound(c Collidable) float64 {
	return imag(c.Position()) + c.Radius()
}

func bottomBound(c Collidable) float64 {
	return imag(c.Position()) - c.Radius()
}

type ByX []Collidable

func (a ByX) Len() int           { return len(a) }
func (a ByX) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByX) Less(i, j int) bool { return leftBound(a[i]) < leftBound(a[j]) }

func DoCollision(a []Collidable) {
	sort.Sort(ByX(a))
	var pairs [][2]Collidable
	for i, left := range a {
		for j := i + 1; j < len(a); j++ {
			right := a[j]
			if leftBound(right) < rightBound(left) {
				if bottomBound(right) < topBound(left) && bottomBound(left) < topBound(right) {
					pairs = append(pairs, [2]Collidable{left, right})
				}
			} else {
				break
			}
		}
	}
	for _, pair := range pairs {
		Collide(pair[0], pair[1])
	}
}
