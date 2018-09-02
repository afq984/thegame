package main

import (
	"github.com/afg984/thegame/server/go/thegame/pb"
)

type ProtoEntity interface {
	ID() int
	Position() complex128
	Radius() float64
	Velocity() complex128
	Health() int
	BodyDamage() int
	RewardingExperience() int
	MaxHealth() int
}

func EntityToProto(e ProtoEntity) *pb.Entity {
	return &pb.Entity{
		Id: int32(e.ID()),
		Position: &pb.Vector{
			X: real(e.Position()),
			Y: imag(e.Position()),
		},
		Radius: e.Radius(),
		Velocity: &pb.Vector{
			X: real(e.Velocity()),
			Y: imag(e.Velocity()),
		},
		Health:              int32(e.Health()),
		BodyDamage:          int32(e.BodyDamage()),
		RewardingExperience: int32(e.RewardingExperience()),
		MaxHealth:           int32(e.MaxHealth()),
	}
}
