import collections
from thegame.abilities import Ability


Vector = collections.namedtuple('Vector', ('x', 'y'))
Vector.__doc__ = '''
A 2D vector.

Used to represent a point and velocity in thegame
'''

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
    '''
    The netural debris.
    '''
    @property
    def edges(self):
        return self.data.edges

class Bullet(Entity):
    '''
    The bullet. Shot from a Hero.
    '''
    def __init__(self, data, hero):
        super().__init__(data)
        self.owner = hero  #: The owner (a ``Hero`` object) of the bullet


HeroAbility = collections.namedtuple(
    'HeroAbility',
    ['level', 'value']
)


HeroAbilityList = collections.namedtuple(
    'HeroAbilityList',
    [ab.as_camel for ab in Ability]
)


class _HeroAbilityShortcut:
    def __init__(self, ability):
        self.ability = ability
        self.__doc__ = \
            f'shortcut to ``hero.abilities.{ability.as_camel}.value``'

    def __get__(self, instance, klass=None):
        if klass is None:
            return self
        return instance.abilities[self.ability].value

    def __set__(self, obj, value):
        raise AttributeError(f'read-only attribute {self.name!r}')


class _HeroAbilityLevelShortcut:
    def __init__(self, ability):
        self.ability = ability
        self.__doc__ = \
            f'shortcut to ``hero.abilities.{ability.as_camel}.level``'

    def __get__(self, instance, klass=None):
        if klass is None:
            return self
        return instance.abilities[self.ability].level

    def __set__(self, obj, value):
        raise AttributeError(f'read-only attribute {self.name!r}')


class _HeroMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases, **kwds):
        return {
            **{
                ab.as_camel: _HeroAbilityShortcut(ab)
                for ab in Ability
            },
            **{
                ab.as_camel + '_level': _HeroAbilityLevelShortcut(ab)
                for ab in Ability
            }
        }


class Hero(Entity, metaclass=_HeroMeta):
    '''
    A Hero is a player in thegame.
    '''
    def __init__(self, data):
        super().__init__(data)

        # we're doing this so it will not be modified accidently
        # maybe not a good way, though.
        self.__dict__['abilities'] = HeroAbilityList(
            *[HeroAbility(*x) for x in zip(
                self.data.ability_levels, self.data.ability_values)]
        )

    @property
    def abilities(self):
        '''
        returns a tuple of abilities.

        Example:
            hero.abilities[MaxHealth].value  # get the value of heros' max health
            hero.abilities.max_health.value  # the same thing

            hero.abilities[MaxHealth].level  # get the ability level
            hero.abilities.max_health.value  # the same thing again
        '''
        return self.__dict__['abilities']
