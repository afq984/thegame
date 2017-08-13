import math
import queue

import grpc

from thegame.entity import Polygon, Bullet, Hero
from thegame import thegame_pb2, thegame_pb2_grpc


class Client:
    def action(self, hero, polygons, heroes, bullets):
        '''
        Implement this method to decide what to do in a turn, given the environment.
        The arguments are passed as keyword arguments.

        :param hero: your hero
        :param list polygons: list of polygons within the field of view
        :param list heroes: list of heroes within the field of view, including yourself
        :param list bullets: list of bullets within the field of view, including those shot from your hero
        '''

    def accelerate(self, x, y):
        '''
        Accelerates towards the point (x, y).

        Repeated calls to this function in a turn will
        overwrite the previous one.
        '''
        self._controls.accelerate = True
        self._controls.acceleration_direction = self._pos_to_dir(x, y)

    def shoot(self, x, y):
        '''
        Shoots a bullet in the current turn, aiming at the point (x, y).
        If bullet is reloading, then nothing will happen.
        Repeated calls to this function in a turn will
        overwrite the previous one.
        '''
        self._controls.shoot = True
        self._controls.shoot_direction = self._pos_to_dir(x, y)

    def level_up(self, ability):
        '''
        Level up the ability in the current turn.
        If there is no skill point available, nothing will happen.
        Repeated calls to this function in a turn will
        make the ability being leveled up multiple times.

        :param thegame.Ability ability: the ability to level up
        '''
        self._controls.level_up.append(ability)

    def _pos_to_dir(self, x, y):
        sx, sy = self._hero.position
        return math.atan2(y - sy, x - sx)

    def _gen(self):
        '''
        Generate requests to grpc
        '''
        yield thegame_pb2.Controls()
        while True:
            controls = self._queue.get()
            yield controls

    def _response_to_controls(self, response):
        polygons = list(map(Polygon, response.polygons))
        heroes = list(map(Hero, response.heroes))
        bullets = list(map(Bullet, response.bullets))
        for hero in heroes:
            if hero.id == response.meta.hero_id:
                break
        else:
            raise Exception('Hero not found')
        self._hero = hero
        self._controls = thegame_pb2.Controls()
        self.action(
            hero=hero,
            polygons=polygons,
            heroes=heroes,
            bullets=bullets)
        return self._controls

    def run(self, remote='localhost:50051'):
        '''
        Start the client
        '''
        channel = grpc.insecure_channel(remote)
        stub = thegame_pb2_grpc.TheGameStub(channel)
        self._queue = queue.Queue()
        request_iterator = self._gen()
        response_iterator = stub.Game(request_iterator)
        for response in response_iterator:
            self._queue.put(self._response_to_controls(response))
