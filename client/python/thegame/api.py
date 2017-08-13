import math
import queue

import grpc

from thegame.entity import Polygon, Bullet, Hero
from thegame import thegame_pb2, thegame_pb2_grpc
from thegame.abilities import Ability


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

    def accelerate(self, direction):
        '''
        Accelerates to the direction (in radians) in the current turn.

        In a turn, only the last call to ``accelerate*`` counts.
        Repeated calls overwrite previous ones.

        :param float direction: The direction to accelerate to, in radians
        '''
        self._controls.accelerate = True
        self._controls.acceleration_direction = direction % math.tau

    def accelerate_towards(self, x, y):
        '''
        Accelerates towards the point (x, y) in the current turn.

        In a turn, only the last call to ``accelerate*`` counts.
        Repeated calls overwrite previous ones.

        :param float x: the absolute x axis
        :param float y: the absolute y axis
        '''
        if (x, y) != self._hero.position:
            self.accelerate(self._pos_to_dir(x, y))

    def shoot(self, direction, *, rotate_only=False):
        '''
        Shoot a bullet in the current turn, aiming at the direction
        (in radians).
        If bullet is reloading, then nothing will happen.

        In a turn, only the last call to ``shoot*`` counts.
        Repeated calls overwrite previous ones.

        :param float direction: the direction to shoot to, in radians
        '''
        self._controls.shoot = not rotate_only
        self._controls.shoot_direction = direction % math.tau

    def shoot_at(self, x, y, *, rotate_only=False):
        '''
        Shoots a bullet in the current turn, aiming at the point (x, y).
        If bullet is reloading, then nothing will happen.

        In a turn, only the last call to ``shoot*`` counts.
        Repeated calls overwrite previous ones.

        :param float x: the absolute x axis
        :param float y: the absolute y axis
        '''
        self.shoot(self._pos_to_dir(x, y), rotate_only=rotate_only)

    def level_up(self, ability):
        '''
        Level up the ability in the current turn.
        If there is no skill point available, nothing will happen.
        Repeated calls to this function in a turn will
        make the ability being leveled up multiple times.

        :param thegame.Ability ability: the ability to level up
        '''
        self._controls.level_up.append(Ability(ability))

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
        channel = grpc.insecure_channel(remote)
        stub = thegame_pb2_grpc.TheGameStub(channel)
        self._queue = queue.Queue()
        request_iterator = self._gen()
        response_iterator = stub.Game(request_iterator)
        for response in response_iterator:
            self._queue.put(self._response_to_controls(response))

    @classmethod
    def main(cls):
        '''
        parse command line arguments and run the client
        '''
        self = cls()
        self._run()
