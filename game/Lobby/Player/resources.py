from typing import TYPE_CHECKING
from enum import Enum, auto
from dataclasses import dataclass

from game.Resources import EWound


if TYPE_CHECKING:
    from .player import Player

__all__ = (
    '_OTD',
    'AlreadyInTeam',
    'EActivity',
    'ETeam',
    'PositionNotFound',
    'AS',
    'Position'
)

class EActivity(Enum):
    Idle = auto() # doing nothing
    ChoosingTeam = auto()
    ChoosingWeapon = auto()
    WatchingInfo = auto()

class ETeam(Enum):
    Shadow = auto()
    Noble = auto()

class AS(Enum):
    Player = auto()
    Enemy = auto()

class AlreadyInTeam(BaseException):
    """Raised when a player wants to switch to a team where he already is."""

class PositionNotFound(BaseException):
    """Raised when there are no more possible positions on the field."""

@dataclass
class _OTD:
    source: 'Player'
    damage: int
    turns: int
    type: EWound

@dataclass
class Position:
    x: int
    y: int

    def __repr__(self) -> str:
        return f'{self.x}, {self.y}'
    
    def __str__(self) -> str:
        return f'{self.x}, {self.y}'

    def set_x(self, x: int) -> 'Position':
        self.x = x
        return self
    
    def set_y(self, y: int) -> 'Position':
        self.y = y
        return self

    def add_x(self, x: int) -> 'Position':
        self.x += x
        return self

    def add_y(self, y: int) -> 'Position':
        self.y += y
        return self