import discord
# import random

import resources as res
from game import Player
from views.abc.fields import V
from .abc import FieldButton, Field
import game


__all__ = (
    'WaitingField',
    'FightField',
    'MovingField'
)

class PlayerButton(FieldButton[V]): # I keep using 'V' to subclass this Button, this class needs to know nothing about its view anyway
    def __init__(self, player: Player, label: str, style: discord.ButtonStyle, disabled: bool = False):
        super().__init__(player, player.Position, label, style=style, force_disable=disabled)
        self.player: Player = player

    async def callback(self, interaction: discord.Interaction):
        await self._show_info(interaction)


class TargetPlayerButton(PlayerButton["FightField"]):
    """Represents a player button. This player may be targeted by an another player's attack."""
    def __init__(
        self,
        player: Player,
        label: str,
        style: discord.ButtonStyle,
        disabled: bool = False
    ):

        super().__init__(player, label, style, disabled)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        if interaction.user != self.player:  # user did not click 'You'
            self.view.target = self.player
            self.view.stop()
            return

        # user clicked 'You'
        await self._show_info(interaction)


class BuffButton(FieldButton[Field]):

    def __init__(
        self,
        buff: game.Buff,
        label: str,
        disabled: bool = True
    ):
        self.buff = buff
        super().__init__(buff, buff.Position, label, force_disable=disabled)

    async def callback(self, interaction: discord.Interaction):
        assert isinstance(self.view, MovingField) # This button should be enabled only in MovingField 
        player: Player = self.view.player
        assert player.Position is not None
        player.Position.set_x(self.buff.Position.x) # type: ignore
        player.Position.set_y(self.buff.Position.y) # type: ignore

        match self.buff.Stat:
            case game.BuffStat.Strength:
                player.Strength += 25
            case game.BuffStat.Armor:
                player.Armor += 15
            case game.BuffStat.Intelligence:
                player.Intelligence += 25
            case game.BuffStat.Perception:
                player.Perception += 15
            case game.BuffStat.Health:
                player.cHealth += 50
            case game.BuffStat.Stamina:
                player.cStamina += 25
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)
        self.view.stop() # type: ignore


class EmptyButton(FieldButton[Field]):
    def __init__(self, position: game.Position, disable: bool = True):
        super().__init__(row=position.y, force_disable=disable)
        self.position = position

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.target = self.position
        self.view.stop() # type: ignore


class FightField(Field):
    """Represents the field of the current player.
    """

    def __init__(
        self,
        player: Player,
        players: list[Player],
        targets: list[Player],
        prob: int,
        buff: game.Buff
    ):

        super().__init__(player, players, prob, buff)
        self.player = player
        self.embed = discord.Embed(
            title="It's your turn"
        )
        if len(targets) == 0:
            self.children[-1].disabled = True
        else:
            self.children[-1].disabled = False

        self.result: res.EResult | None = None
        self.target: Player | None = None
        for x in range(5):
            self._position.set_x(x)
            for y in range(4):
                self._position.set_y(y)

                if self._position in self._placed:
                    placeable = self._placed[self._position]

                    if isinstance(placeable, Player):
                        self.__place_player(placeable, targets)

                    else: 
                        assert isinstance(placeable, game.Buff)
                        self.__place_buff(placeable)

                else:
                    self.add_item(EmptyButton(self._position, disable=True))

    def __place_player(self, placeable: Player, targets: list[Player]):
        label = self._button_label(self.player, placeable)
        disabled = placeable in targets
        style = self._button_style(placeable)

        if placeable == self.player:
            self.add_item(PlayerButton(self.player, label, style, disabled))
        else:
            self.add_item(TargetPlayerButton(placeable, label, style, disabled))

    def __place_buff(self, buff: game.Buff):
        label = self._button_buff_label(buff)
        self.add_item(BuffButton(buff, label))

    @discord.ui.button(label='Back', row=4)
    async def back_btn(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        self.result = res.EResult.Back
        self.stop()

    @discord.ui.button(label='Attack', row=4)
    async def done_btn(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        self.result = res.EResult.Done
        self.stop()


class MovingField(Field):

    def __init__(
        self,
        player: Player,
        players: list[Player],
        prob: int,
        buff: game.Buff
    ):
        
        self.player = player
        self.result: res.EResult | None = None
        self.target: game.Position | None = None

        super().__init__(player, players, prob, buff)
        self.embed = discord.Embed(
            title='Where do you want to move?',
            description='Tap on a location to move there.',
            color=discord.Colour.og_blurple()
        )
        
        for x in range(5):
            self._position.set_x(x)
            for y in range(4):
                self._position.set_y(y)
                if self._position in self._placed:
                    placeable = self._placed[self._position]
                    if isinstance(placeable, game.Buff):
                        self.add_item(BuffButton(placeable, self._button_buff_label(placeable), False))
                    else:
                        assert isinstance(placeable, Player)
                        self.add_item(PlayerButton(placeable, self._button_label(placeable, player), style=self._button_style(placeable)))
                else:
                    self.add_item(EmptyButton(self._position, disable=False))

    @discord.ui.button(label='Back', row=4)
    async def back_btn(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        self.result = res.EResult.Back
        self.stop()


class WaitingField(Field):

    def __init__(
        self,
        player: Player,
        players: list[Player],
        current_player: Player,
        prob: int,
        buff: game.Buff
    ):

        super().__init__(player, players, prob, buff)
        
        self.embed = discord.Embed(title='Field', description=f'Waiting for {current_player.mention}', color=player.color)
        self.embed.set_footer(text='If you click on any player you will see their info.')

        for x in range(5):
            self._position.set_x(x)
            for y in range(4):
                self._position.set_y(y)
                if self._position in self._placed:
                    placeable = self._placed[self._position]
                    if isinstance(placeable, game.Buff):
                        self.add_item(BuffButton(placeable, self._button_buff_label(placeable)))
                    else:
                        assert isinstance(placeable, Player)
                        self.add_item(PlayerButton(placeable, self._button_label(placeable, player), style=self._button_style(placeable)))
                else:
                    self.add_item(EmptyButton(self._position))
