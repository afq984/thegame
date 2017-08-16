package main

import (
	"flag"
	"fmt"
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
	join, err := stream.Recv()
	if err != nil {
		log.Println(err)
		return err
	}
	element := s.arena.Join(join.Name)
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
	gs := NewServer()
	pb.RegisterTheGameServer(s, gs)
	log.Println("listening on", listen)
	go func() {
		for {
			var line string
			fmt.Scanln(&line)
			switch line {
			case "p":
				gs.arena.commandChan <- Pause
			case "r":
				gs.arena.commandChan <- Resume
			default:
				fmt.Printf("Unknown command: %q\n", line)
			}
		}
	}()
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
