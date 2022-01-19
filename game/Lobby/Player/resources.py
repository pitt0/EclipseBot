from typing import TYPE_CHECKING
from enum import Enum, auto
from dataclasses import dataclass

from ...Resources import EStatus

if TYPE_CHECKING:
    from .player import Player

__all__ = (
    '_OTD',
    'AlreadyInTeam',
    'EActivity',
    'ETeam',
    'PositionNotFound'
)

class EActivity(Enum):
    Idle = auto() # doing nothing
    ChoosingTeam = auto()
    ChoosingWeapon = auto()
    WatchingInfo = auto()

class ETeam(Enum):
    Shadow = auto()
    Noble = auto()

class AlreadyInTeam(BaseException):
    """Raised when a player wants to switch to a team where he already is."""

class PositionNotFound(BaseException):
    """Raised when there are no more possible positions on the field."""

@dataclass
class _OTD:
    source: 'Player'
    damage: int
    turns: int
    type: EStatus