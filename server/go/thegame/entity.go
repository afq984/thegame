package main

type Entity struct {
	position complex128
	velocity complex128
	health   int
	visible  bool
	lastHit  Collidable
}

func (e *Entity) Position() complex128 {
	return e.position
}

func (e *Entity) SetPosition(p complex128) {
	e.position = p
}

func (e *Entity) Velocity() complex128 {
	return e.velocity
}

func (e *Entity) SetVelocity(v complex128) {
	e.velocity = v
}

func (e *Entity) Health() int {
	return e.health
}

func (e *Entity) SetHealth(h int) {
	e.health = h
}

func (e *Entity) Visible() bool {
	return e.visible
}

func (e *Entity) SetVisible(v bool) {
	e.visible = v
}

func (e *Entity) LastHit() Collidable {
	return e.lastHit
}

func (e *Entity) SetLastHit(c Collidable) {
	e.lastHit = c
}
