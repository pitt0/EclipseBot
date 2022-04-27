from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable


__all__ = (
    'CostType',
    'Ability'
)


class CostType(Enum):
    Null = auto()
    Health = auto()
    Stamina = auto()


@dataclass
class Ability:
    name: str
    brief: str
    long: str
    cost: int
    cost_type: CostType
    function: Callable[(...), str]
    targets: int
    toggle: bool = False

    def cast(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, __o: object) -> bool:
        return (isinstance(__o, Ability) and self.name == __o.name) or self.name == __o

