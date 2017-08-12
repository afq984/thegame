import abc
import enum


class Skill(enum.IntEnum):
    HealthRegen = 0
    MaxHealth = 1
    BodyDamage = 2
    BulletSpeed = 3
    BulletPenetration = 4
    BulletDamage = 5
    Reload = 6
    MovementSpeed = 7


class Entity(abc.ABC):
    @abc.abstractproperty
    def position(self):
        '''
        The entity's current position in a 2-tuple: (x, y)
        '''

    @abc.abstractproperty
    def velocity(self):
        '''
        The entity's current velocity in a 2-tuple: (x, y)
        '''

    @abc.abstractproperty
    def health(self):
        '''
        The entity's current health, as a non-negative number
        '''


class Client:
    def action(self, debris, heroes, bullets):
        '''
        decide what to do in a turn, given the environment

        debris: list of 拉機
        heroes: list of 敵人
        bullets: list of 敵人的子彈
        '''
        self.level_up(Skill.BodyDamage)

    def accelerate(self, x, y):
        '''
        Accelerates towards the point (x, y).

        Repeated calls to this function in a turn will
        overwrite the previous one.
        '''

    def shoot(self, x, y):
        '''
        Shoots a bullet in the current turn, aiming at the point (x, y)
        If bullet is reloading, then nothing will happen.
        Repeated calls to this function in a turn will
        overwrite the previous one.
        '''

    def level_up(self, ability):
        '''
        Level up the ability.
        If there is no skill point available, nothing will happen.
        Repeated calls to this function in a turn will
        result in ability being leveled up multiple times.
        '''
