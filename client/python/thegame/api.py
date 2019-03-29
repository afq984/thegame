import os
import math
import queue
import secrets
import subprocess
import argparse

import grpc

from thegame.entity import Polygon, Bullet, Hero
from thegame import thegame_pb2 as pb2, thegame_pb2_grpc as pb2_grpc
from thegame.abilities import Ability


Controls = pb2.Controls


class _RequestIterator:
    """
    Helper class to emit streaming grpc requests

    Only supports 1 consumer, may deadlock if more than 1
    """

    _STOP = object()  # ask the queue to stop iterating

    def __init__(self, name):
        self.queue = queue.Queue()
        self.queue.put(pb2.Controls(name=name))
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


def _ready_insecure_channel(address):
    channel = grpc.insecure_channel(address)
    future = grpc.channel_ready_future(channel)
    try:
        future.result(timeout=10)
    except grpc.FutureTimeoutError as e:
        raise Exception(f'Timed out connecting to {address}') from e
    return channel


class LockStepServer:
    def __init__(self, listen=':50051', bin='thegame'):
        """
        listen: address to listen to
        bin: game server command
        """
        self.cmd = [
            bin,
            '--pause', '--must-send-updates',
            f'--listen={listen}',
            f'--terminate-if-parent-is-not={os.getpid()}',
        ]
        self.admin_token = secrets.token_hex()
        self.proc = subprocess.Popen(
            self.cmd,
            stdin=subprocess.DEVNULL,
            env={'THEGAME_ADMIN_TOKEN': self.admin_token, **os.environ},
        )
        host, _, port = listen.partition(':')
        if not host:
            host = 'localhost'
        channel = _ready_insecure_channel(f'{host}:{port}')
        self.stub = pb2_grpc.TheGameStub(channel)

    def terminate(self):
        """
        terminate the server
        """
        self.proc.terminate()

    def _command(self, **kwargs):
        self.stub.Admin(pb2.Command(token=self.admin_token, **kwargs))

    def tick(self):
        """run a tick on the server"""
        self._command(tick=True)

    def wait_for_controls(self):
        """wait for all palyers to send their controls for the current tick"""
        self._command(wait_for_controls=True)

    def reset(self):
        """reset the game"""
        self._command(game_reset=True)


class RawClient:
    def __init__(self, server_address, name):
        channel = _ready_insecure_channel(server_address)
        self.stub = pb2_grpc.TheGameStub(channel)
        self.request_iterator = _RequestIterator(name=name)
        self.response_iterator = self.stub.Game(self.request_iterator)

    def fetch_state(self):
        """
        get the next GameState

        this method blocks until a GameState is available
        """
        return GameState(next(self.response_iterator))

    def send_controls(self, controls: pb2.Controls):
        """
        schedules to send a Controls object to the server

        this method does not block
        """
        self.request_iterator.emit(controls)

    def close(self):
        self.request_iterator.stop()


class GameState:

    __slots__ = ('hero', 'heroes', 'polygons', 'bullets', 'meta')

    def __init__(self, pb2_gs: pb2.GameState):
        self.polygons = list(map(Polygon, pb2_gs.polygons))
        self.bullets = list(map(Bullet, pb2_gs.bullets))
        heroes = []
        self.hero = None
        for rhero in pb2_gs.heroes:
            thero = Hero(rhero)
            if thero.id == pb2_gs.meta.hero_id:
                self.hero = thero
            else:
                heroes.append(thero)
        self.heroes = heroes
        self.meta = pb2_gs.meta
        if self.hero is None:
            raise Exception('player hero not found in hero list')

    def as_dict(self, *, exclude=set()):
        return {
            attr: getattr(self, attr) for attr in self.__slots__
            if attr not in exclude
        }


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
        if (x, y) != self._game_state.hero.position:
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
        sx, sy = self._game_state.hero.position
        return math.atan2(y - sy, x - sx)

    def _action(self, **kwds):
        # warpper to action() to inject stuff
        return self.action(**kwds)

    def _game_state_to_controls(self, gs):
        self._game_state = gs
        self._controls = pb2.Controls()
        self._action(**gs.as_dict(exclude=('meta',)))
        return self._controls

    def run(self):
        remote = self.options.remote

        raw_client = RawClient(remote, getattr(self, 'name', ''))
        try:
            while True:
                game_state = raw_client.fetch_state()
                controls = self._game_state_to_controls(game_state)
                raw_client.send_controls(controls)
        finally:
            raw_client.close()

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
