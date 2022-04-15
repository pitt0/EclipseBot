from typing import TYPE_CHECKING

from .resources import _OTD

from game.Resources import EWound, EStatus, ECondition, EDamage

if TYPE_CHECKING:
    from .player import Player


class OverTimeDamage:

    __slots__ = (
        '_damages',
        'player'
    )

    if TYPE_CHECKING:
        player: Player

    def __init__(self):
        self._damages: list[_OTD] = []

    def set_player(self, player: 'Player'):
        self.player = player

    def _add_wound(self, source: 'Player', damage: int, turns: int, type: EWound):
        self._damages.append(_OTD(source, damage, turns, type))
        match type:
            case EWound.Burn:
                self.player._status._add_condition(ECondition.TakeDamage, EStatus.Burnt)
            case EWound.Wound:
                self.player._status._add_condition(ECondition.TakeDamage, EStatus.Burnt)

    def _end_turn(self):
        dTot = 0
        for _otd in self._damages:
            damage = self.player.TakeDamage(_otd.damage, EDamage.Wound)
            dTot += damage
            _otd.turns -= 1
            if _otd.turns == 0:
                self._damages.remove(_otd)
                match _otd.type:
                    case EWound.Wound if not any(otd.type == EWound.Wound for otd in self._damages):
                        self.player.RemoveStatus(EStatus.Wounded)
                    case EWound.Burn if not any(otd.type == EWound.Burn for otd in self._damages):
                        self.player.RemoveStatus(EStatus.Burnt)

            if not self.player.Alive:
                return dTot
        return dTot