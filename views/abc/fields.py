from typing import TypeVar

import discord

from game import Player, EActivity
from ..info import Info
import game


V = TypeVar('V', bound='discord.ui.View', covariant=True)


class FieldButton(discord.ui.Button[V]):

    def __init__(
        self,
        placeable: game.HasPosition | None = None,
        position: game.Position | None = None,
        label: str = '\u200b',
        row: int = 0,
        style: discord.ButtonStyle = discord.ButtonStyle.grey,
        # This obliges us to explicitating the following parameters when calling the function (in this case the class)
        *,
        force_disable: bool = False,
        force_enable: bool = False
    ) -> None:

        _force = int(force_disable) + int(force_enable)
        assert _force <= 1
        # int(True) returns 1, int(False) returns 0

        self.placeable = placeable
        self.position = position or self.placeable.Position # type: ignore

        if row == 0 and placeable is not None:
            row = placeable.Position.y # type: ignore

        if _force:
            # `if 0` is considered as `if False`, `if 1` is considered as `if True`
            _disabled = force_disable
            # This is enough, since if force_enable was true I would have done
            # _disabled = not force_enable, which returns the result of
            # force_disable
        else:
            _disabled = placeable is None

        super().__init__(label=label, disabled=_disabled, row=row, style=style)

    async def _show_info(self, interaction: discord.Interaction):
        assert type(self.placeable) is Player
        await self.view.disable_buttons()  # type: ignore
        self.placeable.activity = EActivity.WatchingInfo
        info = Info(self.placeable)
        await interaction.response.send_message(embed=info.embed, view=info)
        await info.wait()
        await self.view.enable_buttons()  # type: ignore
        

class Field(discord.ui.View):
    
    def __init__(
        self,
        player: Player,
        players: list[Player],
        prob: int,
        buff: game.Buff,
    ) -> None:
        
        super().__init__(timeout=None)
        self._placed: dict[game.Position, game.HasPosition] = {}
        self._position = game.Position(0, 0)
        self.embed = discord.Embed()

        self._place_players(player.team, players)

        if prob <= 50 and len(self._placed) < 10:
            self._place_buff(buff)
            
                
    def _place_players(self, team: game.ETeam, players: list[Player]):
        for player in players:
            if not player.Alive:
                continue
            if player.Position is None:
                pCoordinates = player.Coordinates(self._placed, game.AS.Player if player.team == team else game.AS.Enemy)
                player.Position = pCoordinates
            self._placed[player.Position] = player

    def _place_buff(self, buff: game.Buff):
        assert buff.Position is not None
        if buff.Position not in self._placed:
            self._placed[buff.Position] = buff

    def _button_label(self, player: Player, current: Player):
        if player == current:
            return 'You'
        
        return current.name[0]
    
    def _button_style(self, player: Player):
        if player.cHealth >= player.Health * 0.75:
            return discord.ButtonStyle.green
        if player.cHealth >= player.Health * 0.25:
            return discord.ButtonStyle.red

        return discord.ButtonStyle.grey

    def _button_buff_label(self, buff: game.Buff):
        match buff.Stat:
            case game.BuffStat.Health:
                return 'Hp +50'
            case game.BuffStat.Stamina:
                return 'St +25'
            case game.BuffStat.Strength | game.BuffStat.Intelligence:
                return f'{buff.Stat.name[:2]} +25'
            case game.BuffStat.Armor | game.BuffStat.Perception:
                return f'{buff.Stat.name[:2]} +15'



    @property
    def children(self) -> list[FieldButton]:
        return super().children # type: ignore

    def enable_buttons(self):
        for child in self.children:
            child.disabled = False

    def disable_buttons(self):
        for child in self.children:
            child.disabled = True