import typing
import queue

import grpc

from thegame.entity import Polygon, Bullet, Hero
from thegame import thegame_pb2, thegame_pb2_grpc


class Client:
    def action(
            self,
            hero: Hero,
            polygons: typing.List[Polygon],
            heroes: typing.List[Hero],
            bullets: typing.List[Bullet]):
        '''
        decide what to do in a turn, given the environment:

        hero is your hero
        polygon is a list of polygons
        heroes is a list of heroes, including yourself
        bullets is a list of bullets, including yours
        '''

    def accelerate(self, x, y):
        '''
        Accelerates towards the point (x, y).

        Repeated calls to this function in a turn will
        overwrite the previous one.
        '''
        self._controls.accelerate = True
        # XXX

    def shoot(self, x, y):
        '''
        Shoots a bullet in the current turn, aiming at the point (x, y)
        If bullet is reloading, then nothing will happen.
        Repeated calls to this function in a turn will
        overwrite the previous one.
        '''
        self._controls.shoot = True
        # XXX self._controls.shoot_direction =

    def level_up(self, ability):
        '''
        Level up the ability.
        If there is no skill point available, nothing will happen.
        Repeated calls to this function in a turn will
        result in ability being leveled up multiple times.
        '''
        self._controls.level_up.append(ability)

    def _gen(self):
        '''
        Generate requests to grpc
        '''
        yield thegame_pb2.Controls()
        while True:
            yield self._queue.get()

    def _turn(self):
        self._controls = thegame_pb2.Controls()
        self.action()

    def run(self, remote='localhost:50051'):
        '''
        Starts the client
        '''
        channel = grpc.insecure_channel(remote)
        stub = thegame_pb2_grpc.TheGameStub(channel)
        self._queue = queue.Queue()
        for response in stub.Game(self._gen()):
            hero = None
            polygons = list(map(Polygon, response.polygons))
            heroes = list(map(Hero, response.heroes))
            bullets = list(map(Bullet, response.bullets))
            self._controls = thegame_pb2.Controls()
            self.action(
                hero=hero,
                polygons=polygons,
                heroes=heroes,
                bullets=bullets)
            self._queue.put(self._controls)

