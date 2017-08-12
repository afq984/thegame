import time
import enum
import grpc

from thegame import thegame_pb2, thegame_pb2_grpc
from thegame.entity import Debris, Bullet, Hero


def gen():
    while True:
        # print('send')
        yield thegame_pb2.Controls()


def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = thegame_pb2_grpc.TheGameStub(channel)
    for response in stub.Game(gen()):
        debris = [Debris(d) for d in response.debris]
        heroes = [Hero(h) for h in response.heroes]
        hero_map = {h.id: h for h in heroes}
        bullets = [Bullet(b, hero_map[b.id]) for b in response.bullets]
