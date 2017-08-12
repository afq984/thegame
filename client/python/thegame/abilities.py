import re
import enum


class Ability(enum.IntEnum):
    HealthRegen = 0
    MaxHealth = 1
    BodyDamage = 2
    BulletSpeed = 3
    BulletPenetration = 4
    BulletDamage = 5
    Reload = 6
    MovementSpeed = 7

    @property
    def as_camel(self):
        return re.sub('([A-Z])', r'_\1', self.name).lstrip('_').lower()
