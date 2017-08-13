import abc
import typing
import math

from thegame.entity import Polygon, Bullet, Hero
from thegame.thegame_pb2 import Controls


class Client(abc.ABC):
    @abc.abstractmethod
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

    def _turn(self):
        self._controls = Controls()
        self.action()

    def accelerate(self, x, y):
        '''
        Accelerates towards the point (x, y).

        Repeated calls to this function in a turn will
        overwrite the previous one.
        '''
        self._controls.accelerate = True
        self._controls.accelerate =

    def shoot(self, x, y):
        '''
        Shoots a bullet in the current turn, aiming at the point (x, y)
        If bullet is reloading, then nothing will happen.
        Repeated calls to this function in a turn will
        overwrite the previous one.
        '''
        self._controls.

    def level_up(self, ability):
        '''
        Level up the ability.
        If there is no skill point available, nothing will happen.
        Repeated calls to this function in a turn will
        result in ability being leveled up multiple times.
        '''
        self._controls.
