import time

import grpc
import collections
from thegame import thegame_pb2, thegame_pb2_grpc


def gen():
    while True:
        # print('send')
        yield thegame_pb2.Controls()


Vector = collections.namedtuple('Vector', ('x', 'y'))


class EntityAttribute:
    def __init__(self, doc=None):
        self.__doc__ = doc

    def __set_name__(self, klass, name):
        self.name = name

    def __get__(self, instance, klass=None):
        if klass is None:
            return self
        return getattr(instance.data.entity, self.name)

    def __set__(self, obj, value):
        raise AttributeError(f'read-only attribute {self.name!r}')

class Entity:
    def __init__(self, data):
        self.data = data

    id = EntityAttribute()

    @property
    def position(self):
        '''
        The velocity of the entity in a 2-tuple (x, y).
        '''
        p = self.data.entity.position
        return Vector(p.x, p.y)

    @property
    def velocity(self):
        '''
        The velocity of the entity in a 2-tuple (x, y).
        '''
        v = self.data.entity.velocity
        return Vector(v.x, v.y)

    radius = EntityAttribute('The radius of the entity')
    health = EntityAttribute(
        '''
        The health of the entity in a non-negative integer.

        When a entity's health is less than or equal to zero it dies.
        '''
    )
    body_damage = EntityAttribute(
        '''
        The body damage of the entity.

        When to entities collide, they reduce each other's health
        with their body damage.
        '''
    )
    rewarding_experience = EntityAttribute(
        '''
        How much experience you will get if you kill this entity.
        '''
    )


class Debris(Entity):
    pass


class Bullet(Entity):
    pass


class HeroAbility:
    def __set_name__(self, klass, name):
        self.name = name

    def __get__(self, instance, klass=None):
        if klass is None:
            return self
        return getattr(instance.data.entity, self.name)

    def __set__(self, obj, value):
        raise AttributeError(f'read-only attribute {self.name!r}')


class Hero(Entity):
    pass


def main():
    channel = grpc.insecure_channel('localhost:50051')
    stub = thegame_pb2_grpc.TheGameStub(channel)
    for response in stub.Game(gen()):
        # print(response)
        d = Debris(response.debris[0])
        print(d.position, d.velocity, d.health, d.body_damage, d.radius)
