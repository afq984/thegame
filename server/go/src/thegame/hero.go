package main

import "math"
import "math/cmplx"
import "thegame/pb"

type Bullet struct {
	Entity
	owner   *Hero
	timeout int
}

func (b *Bullet) Friction() float64 {
	return 0
}

func (b *Bullet) IsBounded() bool {
	return false
}

func (b *Bullet) MaxSpeed() float64 {
	return math.Inf(1)
}

func (b *Bullet) Radius() float64 {
	return 20
}

func (b *Bullet) Team() int {
	return b.owner.Team()
}

func (b *Bullet) BodyDamage() int {
	return b.owner.ability(BulletDamage)
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

type Hero struct {
	Entity
	id int

	score         int
	experience    int
	skillPoints   int
	level         int
	abilityLevels [NAbilities]int
	orientation   float64
	cooldown      int

	controls pb.Controls
}

func (h *Hero) Friction() float64 {
	return 0.1
}

func (h *Hero) IsBounded() bool {
	return true
}

func (h *Hero) MaxSpeed() float64 {
	return float64(h.ability(MovementSpeed))
}

func (h *Hero) Radius() float64 {
	return 30
}

func (h *Hero) Team() int {
	return h.id
}

func (h *Hero) ability(a int) int {
	return AbilityValues[a][h.abilityLevels[a]]
}

func (h *Hero) BodyDamage() int {
	return h.ability(BodyDamage)
}

func (h *Hero) AcquireExperience(e int) {
	h.score += e
	h.experience += e
	for h.experience >= experienceToLevelUp(h.level) {
		h.experience -= experienceToLevelUp(h.level)
		h.level++
		h.skillPoints++
	}
}

func (h *Hero) RewardingExperience() int {
	return h.score / 2
}

func (h *Hero) Shoot() *Bullet {
	return &Bullet{
		Entity: Entity{
			health:   h.ability(BulletPenetration),
			position: h.position + h.velocity + cmplx.Rect(h.Radius(), h.orientation),
			velocity: cmplx.Rect(float64(h.ability(BulletSpeed)), h.orientation),
			visible:  true,
		},
		timeout: 100,
	}
}

// Action performs the action for the current tick on the given arena
func (h *Hero) Action(a *Arena) {
	if h.cooldown > 0 {
		h.cooldown--
	} else if h.controls.Shoot {
		bullet := h.Shoot()
		a.bullets = append(a.bullets, bullet)
		h.cooldown = h.ability(Reload)
	}
	if h.health > 0 {
		h.health += h.ability(HealthRegen)
		if h.health > h.ability(MaxHealth) {
			h.health = h.ability(MaxHealth)
		}
	}
	if h.controls.Accelerate {
		h.velocity += cmplx.Rect(0.6, h.controls.AccelerationDirection)
	}
}
