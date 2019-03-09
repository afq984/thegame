package main

import (
	"errors"
	"flag"
	"fmt"
	"log"
	"net"
	"os"

	"google.golang.org/grpc"

	"github.com/afg984/thegame/server/go/thegame/pb"
)

var listen string

func init() {
	flag.StringVar(&listen, "listen", ":50051", "[host]:port to listen to")
}

type server struct {
	arena          *Arena
	spectatorToken string
	adminToken     string
}

func NewServer() *server {
	s := &server{
		arena:          NewArena(),
		spectatorToken: os.Getenv("THEGAME_SPECTATOR_TOKEN"),
		adminToken:     os.Getenv("THEGAME_ADMIN_TOKEN"),
	}
	if s.adminToken == "" {
		log.Println("Environment variable THEGAME_ADMIN_TOKEN is not set or empty," +
			" admin command is disabled")
	}
	return s
}

func (s *server) Game(stream pb.TheGame_GameServer) error {
	log.Println("New client connected")
	join, err := stream.Recv()
	if err != nil {
		log.Printf("join initialization failed: %v", err)
		return err
	}
	element := s.arena.Join(join.Name)
	hero := element.Value.(*Hero)
	go func() {
		updates := hero.UpdateChan
		for gameState := range updates {
			err := stream.Send(gameState)
			if err != nil {
				log.Printf("cannot send gameState to %v: %v", hero, err)
			}
		}
	}()
	defer s.arena.Quit(element)
	for {
		controls, err := stream.Recv()
		if err != nil {
			log.Printf("cannot receive controls from %v: %v", hero, err)
			return err
		}
		s.arena.controlChan <- HeroControls{
			Hero:     hero,
			Controls: controls,
		}
	}
}

func (s *server) View(view *pb.ViewRequest, stream pb.TheGame_ViewServer) error {
	if s.spectatorToken != view.Token {
		return errors.New("Invalid token")
	}
	ch := make(chan *pb.GameState, 16)
	s.arena.viewChan <- ch
	for gs := range ch {
		err := stream.Send(gs)
		if err != nil {
			log.Printf("cannot send gameState to audience: %v", err)
			return err
		}
	}
	return nil
}

func (s *server) Admin(stream pb.TheGame_AdminServer) error {
	auth, err := stream.Recv()
	if err != nil {
		log.Printf("Cannot receive command: %v", err)
		return err
	}
	if s.adminToken == "" {
		return errors.New("Admin disabled")
	}
	if auth.Token != s.adminToken {
		return errors.New("Invalid token")
	}
	for {
		command, err := stream.Recv()
		if err != nil {
			log.Println("Failed to recv admin command: %v", command)
			return err
		}
		if command.Resume {
			s.arena.commandChan <- CommandResume
		}
		if command.Pause {
			s.arena.commandChan <- CommandPause
		}
		if command.Tick {
			s.arena.commandChan <- CommandTick
		}
		err = stream.Send(&pb.CommandResponse{})
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
				gs.arena.commandChan <- CommandPause
			case "r":
				gs.arena.commandChan <- CommandResume
			case "t":
				gs.arena.commandChan <- CommandTick
			default:
				fmt.Printf("Unknown command: %q\n", line)
			}
		}
	}()
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
