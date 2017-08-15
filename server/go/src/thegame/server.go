package main

import (
	"flag"
	"log"
	"net"

	_ "golang.org/x/net/context"
	"google.golang.org/grpc"

	"thegame/pb"
)

var listen string

func init() {
	flag.StringVar(&listen, "listen", ":50051", "[host]:port to listen to")
}

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
	hero := element.Value.(*Hero)
	go func() {
		updates := hero.UpdateChan
		for gameState := range updates {
			err := stream.Send(gameState)
			if err != nil {
				log.Println(err)
			}
		}
	}()
	defer s.arena.Quit(element)
	for {
		controls, err := stream.Recv()
		if err != nil {
			log.Println(err)
			return err
		}
		s.arena.controlChan <- HeroControls{
			Hero:     hero,
			Controls: controls,
		}
	}
}

func main() {
	flag.Parse()
	lis, err := net.Listen("tcp", listen)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterTheGameServer(s, NewServer())
	log.Println("listening on", listen)
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
