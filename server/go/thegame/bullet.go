package main

import (
	"fmt"
	"math"

	"github.com/afg984/thegame/server/go/thegame/pb"
)

type Bullet struct {
	Entity
	owner   *Hero
	timeout int
	id      int
}

func (b *Bullet) ToProto() *pb.Bullet {
	return &pb.Bullet{
		Entity: EntityToProto(b),
		Owner:  int32(b.owner.id),
	}
}

func (b *Bullet) String() string {
	return fmt.Sprintf("Bullet#%d:%s", b.id, b.owner)
}

func (b *Bullet) ID() int {
	return b.id
}

func (b *Bullet) MaxHealth() int {
	return b.owner.ability(BulletPenetration)
}

func (b *Bullet) Friction() float64 {
	return 0.02
}

func (b *Bullet) IsBounded() bool {
	return false
}

func (b *Bullet) MaxSpeed() float64 {
	return math.Inf(1)
}

func (b *Bullet) Radius() float64 {
	return 10
}

func (b *Bullet) Team() int {
	return b.owner.Team()
}

func (b *Bullet) BodyDamage() int {
	return b.owner.ability(BulletDamage)
}

func (b *Bullet) CanAcquireExperience() bool {
	return true
}

func (b *Bullet) AcquireExperience(e int) {
	b.owner.AcquireExperience(e)
}

func (b *Bullet) RewardingExperience() int {
	return 0
}

func experienceToLevelUp(level int) int {
	return int(10 * math.Pow(1.2, float64(level)))
}
