from dataclasses import dataclass
from enum import Enum, auto

from .resources import Position

class BuffStat(Enum):
    Health = auto()
    Stamina = auto()
    Strength = auto()
    Armor = auto()
    Intelligence = auto()
    Perception = auto()

@dataclass
class Buff:
    Position: Position | None
    Stat: BuffStat