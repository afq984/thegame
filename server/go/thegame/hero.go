package main

import (
	"fmt"
	"log"
	"math/cmplx"

	"github.com/afg984/thegame/server/go/thegame/pb"
)

type Hero struct {
	Entity

	score               int
	experience          int
	skillPoints         int
	level               int
	abilityLevels       [NAbilities]int
	orientation         float64
	cooldown            int
	healthRegenCooldown int
	id                  int
	name                string
	respawnCooldown     int

	controls     *pb.Controls
	disconnected bool
	UpdateChan   chan *pb.GameState
}

func (h *Hero) ToProto() *pb.Hero {
	levels := make([]int32, 8)
	values := make([]int32, 8)
	for i, level := range h.abilityLevels {
		levels[i] = int32(level)
		values[i] = int32(AbilityValues[i][level])
	}
	return &pb.Hero{
		Entity:              EntityToProto(h),
		AbilityLevels:       levels,
		AbilityValues:       values,
		Orientation:         h.orientation,
		Level:               int32(h.level),
		Score:               int32(h.score),
		Experience:          int32(h.experience),
		ExperienceToLevelUp: int32(experienceToLevelUp(h.level)),
		SkillPoints:         int32(h.skillPoints),
		Cooldown:            int32(h.cooldown),
		HealthRegenCooldown: int32(h.healthRegenCooldown),
		Name:                h.name,
	}
}

type ByScore []*pb.ScoreEntry

func (a ByScore) Len() int           { return len(a) }
func (a ByScore) Less(i, j int) bool { return a[i].Score > a[j].Score }
func (a ByScore) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }

func (h *Hero) ToScoreEntry() *pb.ScoreEntry {
	return &pb.ScoreEntry{
		HeroId:   int32(h.id),
		HeroName: h.name,
		Score:    int32(h.score),
		Level:    int32(h.level),
	}
}

func NewHero(id int, name string) *Hero {
	if name == "" {
		name = fmt.Sprintf("Hero#%d", id)
	}
	return &Hero{
		level:      1,
		name:       name,
		id:         id,
		UpdateChan: make(chan *pb.GameState, 1),
	}
}

func (h *Hero) ID() int {
	return h.id
}

func (h *Hero) String() string {
	return fmt.Sprintf("Hero#%d", h.id)
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

func (h *Hero) CanAcquireExperience() bool {
	return true
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

func (h *Hero) MaxHealth() int {
	return h.ability(MaxHealth)
}

func (h *Hero) SetHealth(health int) {
	if health < h.health {
		h.healthRegenCooldown = 50
	}
	h.health = health
}

// Shoot creates a bullet from the hero's stats
// After shooting, remember to assign a bullet id
func (h *Hero) Shoot() *Bullet {
	return &Bullet{
		Entity: Entity{
			health:   h.ability(BulletPenetration),
			position: h.position + cmplx.Rect(h.Radius()+10+1, h.orientation),
			velocity: cmplx.Rect(float64(h.ability(BulletSpeed)), h.orientation),
			visible:  true,
		},
		owner:   h,
		timeout: 120,
	}
}

// Action performs the action for the current tick on the given arena
func (h *Hero) Action(a *Arena) {
	if h.controls == nil {
		return // TODO
	}
	h.orientation = h.controls.ShootDirection
	if h.cooldown > 0 {
		h.cooldown--
	} else if h.controls.Shoot {
		bullet := h.Shoot()
		a.bulletCounter++
		bullet.id = a.bulletCounter
		a.bullets = append(a.bullets, bullet)
		h.cooldown = h.ability(Reload)
	}
	if h.health > 0 {
		if h.healthRegenCooldown > 0 {
			h.healthRegenCooldown--
		} else {
			h.health += h.ability(HealthRegen)
			if h.health > h.ability(MaxHealth) {
				h.health = h.ability(MaxHealth)
			}
		}
	}
	for _, skill := range h.controls.LevelUp {
		if h.skillPoints <= 0 {
			break
		}
		if h.abilityLevels[skill] < 8 {
			h.abilityLevels[skill]++
			h.skillPoints--
		}
	}
	if h.controls.Accelerate {
		h.velocity += cmplx.Rect(h.MaxSpeed()/10, h.controls.AccelerationDirection)
	}
}

func (h *Hero) Spawn(a *Arena) {
	experience := h.score / 3
	h.score = 0
	h.experience = 0
	h.skillPoints = 0
	h.level = 1
	for i := range h.abilityLevels {
		h.abilityLevels[i] = 0
	}
	h.cooldown = 0
	h.healthRegenCooldown = 0
	h.health = h.MaxHealth()
	h.visible = true
	h.AcquireExperience(experience)
	h.position = a.RandomPosition()
	h.velocity = 0
	h.lastHit = nil
	h.respawnCooldown = 180
	log.Println(h, "spawned at", h.position)
}

// ReadyToSpawn marks the hero ready to spawn on the next tick
func (h *Hero) ReadyToSpawn() {
	h.health = 0
	h.visible = false
	h.respawnCooldown = 0
}

// TryRespawn checks for the respawn cooldown, and if it is 0,
// respawn the hero
func (h *Hero) TryRespawn(a *Arena) {
	if h.respawnCooldown == 0 {
		h.Spawn(a)
	} else {
		h.respawnCooldown--
	}
}
