from enum import Enum, auto

__all__ = (
    'EWeaponType',
    'EDamage',
    'EHeal',
    'EArrowType',
    'EStatus',
    'EWound',
    'ECondition'
)

class EWeaponType(Enum):
    Idle = 0
    Shadwoed = 1
    Noble = 2

class EDamage(Enum):
    BaseAttack = auto()
    Ability = auto()
    TrueDamage = auto()
    Wound = auto()

class EHeal(Enum):
    Normal = auto()
    Cursed = auto()

class EArrowType(Enum):
    Normal = auto()
    Electrical = auto()
    Ablaze = auto()
    Frozen = auto()

class ECondition(Enum):
    Attacking = auto()
    TakeDamage = auto()
    Targeting = auto()

class EStatus(Enum):
    Blinded = auto()
    Burnt = auto()
    Disarmed = auto()
    Stunned = auto()
    Targeted = auto()
    Transferred = auto()
    Untouchable = auto()
    Wounded = auto()

class EWound(Enum):
    Burn = auto()
    Heal = auto()
    Wound = auto()