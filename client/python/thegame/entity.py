import collections
from thegame.abilities import Ability


Vector = collections.namedtuple('Vector', ('x', 'y'))
Vector.__doc__ = '''
A 2D vector.

Used to represent a point and velocity in thegame
'''


class _EntityAttribute:
    def __init__(self, doc=None):
        self.__doc__ = doc

    def __set_name__(self, klass, name):
        self.name = name

    def __get__(self, instance, klass=None):
        if instance is None:
            return self
        return getattr(instance.data.entity, self.name)

    def __set__(self, obj, value):
        raise AttributeError(f'read-only attribute {self.name!r}')


class _DataAttribute:
    def __init__(self, doc=None):
        self.__doc__ = doc

    def __set_name__(self, klass, name):
        self.name = name

    def __get__(self, instance, klass=None):
        if instance is None:
            return self
        return getattr(instance.data, self.name)

    def __set__(self, obj, value):
        raise AttributeError(f'read-only attribute {self.name!r}')


class Entity:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}#{self.id} '
            f'BD={self.body_damage} '
            f'HP={self.health}/{self.max_health} '
            f'@({self.position.x:.0f},{self.position.y:.0f})>'
        )

    id = _EntityAttribute('The id of the entity')

    @property
    def position(self):
        '''
        The position of the entity in a 2-tuple (x, y).
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

    radius = _EntityAttribute('The radius of the entity')
    health = _EntityAttribute(
        '''
        The health of the entity in a non-negative integer.

        When a entity's health is less than or equal to zero it dies.
        And the one dealing the killing blow is rewarded with
        ``rewarding_experience``.
        '''
    )
    body_damage = _EntityAttribute(
        '''
        The body damage of the entity.

        When two entities collide, they reduce each other's health
        with their body damage.
        '''
    )
    rewarding_experience = _EntityAttribute(
        '''
        How much experience you will get if you kill this entity.
        '''
    )
    max_health = _EntityAttribute(
        '''
        The maximum health of this entity.
        '''
    )


class Polygon(Entity):
    '''
    The netural polygons.
    '''
    @property
    def edges(self):
        '''
        How many edges does the polygon have
        '''
        return self.data.edges


class Bullet(Entity):
    '''
    The bullet. Shot from a Hero.
    '''

    @property
    def owner_id(self):
        '''
        The id of the hero owning the bullet
        '''
        return self.data.owner


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
        if instance is None:
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
        if instance is None:
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

        Example::

            hero.abilities[MaxHealth].value  # get the hero's max health
            hero.abilities.max_health.value  # the same thing

            hero.abilities[MaxHealth].level  # get the ability level
            hero.abilities.max_health.level  # the same thing again
        '''
        return self.__dict__['abilities']

    orientation = _DataAttribute(
        '''
        The orientation of the hero; the direction the barrel is facing at,
        in radians.
        '''
    )
    level = _DataAttribute('The level of the hero')
    score = _DataAttribute('The score of the hero')
    experience = _DataAttribute('The experience the hero has')
    experience_to_level_up = _DataAttribute(
        'The experience required for the hero to level up')
    skill_points = _DataAttribute(
        'Number of skill points available to level up abilities'
    )
    cooldown = _DataAttribute(
        '''
        How many ticks until a bullet is ready.
        Increase the *reload* ability to reduce the cooldown.

        ``shoot`` and ``shoot_at`` can still be called when on cooldown, but
        nothing will happen instead.
        '''
    )
    health_regen_cooldown = _DataAttribute(
        '''
        How many ticks until the hero can start to regenerate health
        '''
    )
    name = _DataAttribute(
        '''
        The name of the hero. Not guranteed to be unique
        '''
    )
