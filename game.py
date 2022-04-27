from core import Player

import core

class Turn: pass


class Game:
    __slots__ = ()

    players: list[Player]
    turn: Turn

    async def start(self) -> None:
        ...

    async def change_players_state(self, status: core.EActivity) -> None:
        for player in self.players:
            player.activity = status

    async def init_lobby(self) -> list[Player]:
        ...