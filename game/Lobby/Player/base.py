from typing import Protocol
from .resources import Position

class HasPosition(Protocol):
    """Whatever occupies a position on the field."""
    Position: Position | None
