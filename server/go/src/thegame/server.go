package main

import (
	"fmt"
	"log"
	"net"
	"sync"

	_ "golang.org/x/net/context"
	"google.golang.org/grpc"

	"thegame/pb"
)

const (
	port = ":50051"
)

type server struct {
	sync.Mutex
	clients map[int]bool
}

func NewServer() *server {
	return &server{
		clients: make(map[int]bool),
	}
}

func (s *server) registerClient(client int) {
	defer s.Unlock()
	s.Lock()
	s.clients[client] = true
}

func (s *server) unregisterClient(client int) {
	defer s.Unlock()
	s.Lock()
	delete(s.clients, client)
}

func (s *server) Game(stream pb.TheGame_GameServer) error {
	for {
		controls, err := stream.Recv()
		if err != nil {
			log.Println("error", err)
			return err
		}
		fmt.Println(controls)
		if err := stream.Send(&pb.GameState{Response: "yo"}); err != nil {
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
