package main

import (
	"log"
	"net"

	_ "golang.org/x/net/context"
	"google.golang.org/grpc"

	"thegame/pb"
)

const (
	port = ":50051"
)

type server struct {
	arena *Arena
}

func NewServer() *server {
	return &server{
		arena: NewArena(),
	}
}

func (s *server) Game(stream pb.TheGame_GameServer) error {
	log.Println("New client connected")
	element := s.arena.Join()
	go func() {
		updates := element.Value.(*Hero).UpdateChan
		for gameState := range updates {
			err := stream.Send(gameState)
			if err != nil {
				log.Println(err)
			}
		}
	}()
	defer s.arena.Quit(element)
	for {
		_, err := stream.Recv()
		if err != nil {
			log.Println(err)
			return err
		}
	}
}

func main() {
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterTheGameServer(s, NewServer())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
