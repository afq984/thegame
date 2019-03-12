import math
import queue
import argparse

import grpc

from thegame.entity import Polygon, Bullet, Hero
from thegame import thegame_pb2, thegame_pb2_grpc
from thegame.abilities import Ability


class RequestIterator:
    """
    Helper class to emit streaming grpc requests

    Only supports 1 consumer, may deadlock if more than 1
    """

    _STOP = object()  # ask the queue to stop iterating

    def __init__(self, name):
        self.queue = queue.Queue()
        self.queue.put(thegame_pb2.Controls(name=name))
        self.stopped = False

    def __next__(self):
        if self.stopped:
            raise StopIteration
        obj = self.queue.get()
        if obj is self._STOP:
            self.stopped = True
            raise StopIteration
        return obj

    def emit(self, obj):
        self.queue.put(obj)

    def stop(self):
        self.queue.put(self._STOP)


class HeadlessClient:
    def __init__(self):
        super().__init__()
        self._controls = None
        self.init()

    def init(self):
        '''
        This method is called when the client is constructed

        If you want to initialize the client, put the code here.

        To set the name of your hero, set it here like::

            self.name = 'yo'
        '''

    def action(self, hero, heroes, polygons, bullets):
        '''
        Implement this method to decide what to do in a turn, given the environment.
        The arguments are passed as keyword arguments.

        :param hero: your hero
        :param list heroes: list of heroes within the field of view, does not
                            include yourself
        :param list polygons: list of polygons within the field of view
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
        yield thegame_pb2.Controls(name=getattr(self, 'name', ''))
        while True:
            controls = self._queue.get()
            if controls is Stop:
                break
            yield controls

    def _action(self, **kwds):
        # warpper to action() to inject stuff
        return self.action(**kwds)

    def _response_to_objects(self, response):
        polygons = list(map(Polygon, response.polygons))
        bullets = list(map(Bullet, response.bullets))
        heroes = []
        self._hero = None
        for rhero in response.heroes:
            thero = Hero(rhero)
            if thero.id == response.meta.hero_id:
                self._hero = thero
            else:
                heroes.append(thero)
        if self._hero is None:
            raise Exception('player hero not found in hero list')
        return dict(
            hero=self._hero,
            heroes=heroes,
            polygons=polygons,
            bullets=bullets,
        )

    def _response_to_controls(self, response):
        objects = self._response_to_objects(response)
        self._controls = thegame_pb2.Controls()
        self._action(**objects)
        return self._controls

    def run(self):
        remote = self.options.remote

        channel = grpc.insecure_channel(remote)
        stub = thegame_pb2_grpc.TheGameStub(channel)
        try:
            request_iterator = RequestIterator(name=getattr(self, 'name', ''))
            response_iterator = stub.Game(request_iterator)
            for response in response_iterator:
                self._game_state = response
                request_iterator.emit(self._response_to_controls(response))
        finally:
            request_iterator.stop()

    @classmethod
    def _configure_parser(cls, parser):
        parser.add_argument(
            'remote',
            nargs='?',
            default='localhost:50051',
            help='the location of the server'
        )

    def _parse_args(self):
        parser = argparse.ArgumentParser(allow_abbrev=False)
        self._configure_parser(parser)
        self.options = parser.parse_args()

    @classmethod
    def main(cls):
        '''
        parse command line arguments and run the client
        '''
        self = cls()
        self._parse_args()
        self.run()
