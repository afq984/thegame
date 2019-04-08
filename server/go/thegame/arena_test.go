package main

import (
	"os"
	"testing"

	"github.com/afg984/thegame/server/go/thegame/pb"

	"github.com/golang/protobuf/proto"
)

func TestMain(m *testing.M) {
	mustSendUpdates = true
	startGameAsPaused = true
	os.Exit(m.Run())
}

func normalizeGameState(gs *pb.GameState) *pb.GameState {
	copy := proto.Clone(gs).(*pb.GameState)
	for _, p := range copy.Polygons {
		p.Entity.Id = 0
	}
	for _, b := range copy.Bullets {
		b.Entity.Id = 0
	}
	return copy
}

func gameStateEqual(a *pb.GameState, b *pb.GameState) bool {
	return proto.Equal(normalizeGameState(a), normalizeGameState(b))
}

func TestResetIsDeterministic(t *testing.T) {
	a := NewArena()
	heroHandle := a.Join("player")
	a.Command(CommandTick)
	gs1 := <-heroHandle.UpdateChan()
	a.Command(CommandReset)
	a.Seed(1)
	a.Command(CommandTick)
	gs2 := <-heroHandle.UpdateChan()
	if !gameStateEqual(gs1, gs2) {
		t.Error("game reset with same seed produced different results")
	}
}

func TestResetIsDeterministicForMultiPlayer(t *testing.T) {
	const N = 5
	a := NewArena()
	heroHandles := [N]*HeroHandle{
		a.Join("p0"),
		a.Join("p1"),
		a.Join("p2"),
		a.Join("p3"),
		a.Join("p4"),
	}
	a.Command(CommandTick)
	var gameStates1 [N]*pb.GameState
	for i, handle := range heroHandles {
		gameStates1[i] = <-handle.UpdateChan()
	}
	a.Command(CommandReset)
	a.Seed(1)
	a.Command(CommandTick)
	for i, handle := range heroHandles {
		gs2 := <-handle.UpdateChan()
		if !gameStateEqual(gameStates1[i], gs2) {
			t.Errorf("game reset with same seed produced different results for %v", handle)
			t.Log(gameStates1[i])
			t.Log(gs2)
		}
	}
}
