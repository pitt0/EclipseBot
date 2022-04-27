import discord

from .field import *
from core import Player

import resources as res
import core

__all__ = (
    'AbilityButton', 
    'MoveChoice',
    'Attack'
)


class AbilityButton(discord.ui.Button['VAbilities']):
    """Represents an ability Button

    Parameters
    ---
    ability :class:`str`
        The ability name
    disabled :class:`bool`
        Whether the ability is clickable or not
    """
    def __init__(self, ability: core.Ability, disabled: bool):
        super().__init__(label=str(ability), row=0, disabled=disabled)
        self.ability = ability

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        assert self.label is not None

        players = self.view.players
        
        attack = Attack(self.view, self.ability, self.view.player, players)
        await interaction.response.edit_message(embed=attack.embed, view=attack)
        await attack.wait()

        if attack.result is res.EResult.Back:
            return

        allies = [player for player in players if player.team == player.team and player != self.view.player and player.Alive]
        match self.ability.targets:
            case -2:
                targets = [enemy for enemy in self.view.enemies if enemy.cHealth < enemy.Health]
                self.view.result = self.ability.cast(targets, allies)
            case -1:
                self.view.result = self.ability.cast(self.view.enemies, allies)
            case 0:
                self.view.result = self.ability.cast(None, allies)
            case _:
                targets: list[Player] = []
                while len(targets) < self.ability.targets:
                    field = FightField(self.view.player, self.view.players, targets, self.view.previous.prob, self.view.previous.buff)
                    await interaction.message.edit(embed=field.embed, view=field) # type: ignore
                    await field.wait()
                    match field.result:
                        case res.EResult.Back:
                            try:
                                targets.pop(-1)
                                continue
                            
                            except IndexError:
                                previous = self.view.previous
                                await interaction.message.edit(embed=previous.embed, view=previous) # type: ignore
                                return self.view.stop()

                        case res.EResult.Done:
                            if len(targets) == 0:
                                continue
                            break
                        case _:
                            assert field.target is not None
                            targets.append(field.target)
                
                if self.ability.targets == 1:
                    self.view.result = self.ability.cast(targets[0], allies)
                else:
                    self.view.result = self.ability.cast(targets, allies)

        await self.view.wait_for_players()
        self.view.stop()


class VAbilities(discord.ui.View):
    """A wrapper for player's abilities"""

    def __init__(
        self,
        previous_view: 'MoveChoice',
        player: Player,
        allies: list[Player],
        enemies: list[Player],
        players: list[Player]
    ):
        super().__init__(timeout=None)
        
        self.previous = previous_view
        self.embed = discord.Embed(title='Abilities', description='Make your choice', color=player.color)
        self.embed.set_footer(text='A disabled button means that you have no enouhg stamina')
        self.user_messages: list[discord.Message] = []

        self.player = player
        abilities = player.Abilities
        for ability in abilities:
            disabled = False
            match ability.cost_type:
                case core.CostType.Stamina:
                    disabled = self.player.cStamina < ability.cost
                case core.CostType.Health:
                    disabled = self.player.cHealth < ability.cost

            if isinstance(player.Weapon, core.SharpenedKatana):
                print(player.Weapon.UsedAbilities)
                if ability in player.Weapon.UsedAbilities:
                    disabled = True
                self.embed.set_footer(text='A disabled button means that you have no enouhg stamina or you already used this ability.\nYou must use all the ability once before you can use one twice.')

            self.add_item(AbilityButton(ability, disabled))

        self.allies = allies
        self.enemies = enemies
        self.players = players

        self.result: str = None # type: ignore

    @property
    def children(self) -> list[discord.ui.Button]:
        return [child for child in super().children if isinstance(child, discord.ui.Button)]


    @discord.ui.button(label='<<')
    async def back_btn(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(embed=self.previous.embed, view=self.previous)
        self.stop()

    async def enable_buttons(self, disable: bool = False):
        for child in self.children:
            child.disabled = disable

    async def wait_for_players(self):
        await self.wait_players()
        for player in self.players:
            await player.wait()
        await self._done()

    async def wait_players(self):
        await self.enable_buttons(disable=True)
        for player in self.players:
            self.user_messages.append(await player.send('Waiting for other players...'))

    async def _done(self):        
        await self.enable_buttons(disable=False)
        for message in self.user_messages:
            await message.delete()
        self.user_messages = []


class MoveChoice(discord.ui.View):
    """The prompt from where the current player will choose what to do.
    
    Parameters
    ---
    player :class:`Player`
        The user's Player.
    players :class:`list[Player]`
        The whole lobby of players

    Attributes
    ---
    embed :class:`discord.Embed`
        The embed of the prompt. 
    result :class:`EResult`
        The result of player's action.
    """

    def __init__(self, player: Player, players: list[Player], prob: int, buff: core.Buff):
        super().__init__(timeout=None)
        self.player = player
        self.allies = [pl for pl in players if pl.team == player.team and player != pl]
        self.enemies = [pl for pl in players if pl.team != player.team]
        self.lobby = players
        
        self.prob = prob
        self.buff = buff

        self.user_messages: list[discord.Message] = []

        self.embed = discord.Embed(title='Your Turn', description='Make your choice', color=player.color)
        self.embed.add_field(name='Base Attack', value=player.Weapon.Abilities[0], inline=False)
        for ability in player.Abilities:
            self.embed.add_field(name=ability, value=ability.brief, inline=False)

        self.result: str = None # type: ignore

    @property
    def children(self) -> list[discord.ui.Button]:
        return super().children # type: ignore

    def enable_buttons(self):
        for child in self.children:
            child.disabled = False

    def disable_buttons(self):
        for child in self.children:
            child.disabled = True

    async def wait(self):
        await super().wait()
        await self.alert_players()
        for player in self.lobby:
            await player.wait()
        await self._done()

    async def alert_players(self):
        self.disable_buttons()
        for player in self.lobby:
            self.user_messages.append(await player.send('Waiting for other players...'))

    async def _done(self):
        self.enable_buttons()
        for message in self.user_messages:
            await message.delete()
        self.user_messages = []

    @discord.ui.button(label="Base Attack")
    async def BaseAttack(self, interaction: discord.Interaction, _):
    
        await interaction.response.defer()
        await self.wait()
        ability = self.player.Abilities[0]

        attack = Attack(self, ability, self.player, self.lobby)
        await interaction.followup.edit_message(interaction.message.id, embed=attack.embed, view=attack) # type: ignore
        await attack.wait()
        await self.wait()

        if attack.result is res.EResult.Back:
            return

        
        field = FightField(self.player, self.lobby, [], self.prob, self.buff)
        await interaction.followup.edit_message(interaction.message.id, embed=field.embed, view=field) # type: ignore
        await field.wait()
        await self.wait()
        assert field.target is not None
        self.result = self.player.BaseAttack(field.target)
        
        self.stop()
        
    @discord.ui.button(label="Ability")
    async def Ability(self, interaction: discord.Interaction, _):
        abilities = VAbilities(self, self.player, self.allies, self.enemies, self.lobby)
        await interaction.response.edit_message(embed=abilities.embed, view=abilities)
        await abilities.wait()
        if abilities.result is None:
            return

        self.result = abilities.result
        self.stop()

    @discord.ui.button(label='Move')
    async def Move(self, interaction: discord.Interaction, _):

        await interaction.response.defer()
        await self.wait()
        
        field = MovingField(self.player, self.lobby, self.prob, self.buff)
        await interaction.followup.edit_message(interaction.message.id, embed=field.embed, view=field) # type: ignore
        await field.wait()
        if field.result is res.EResult.Back:
            return 

        await self.wait()
        self.result = f"{self.player.name} moved to position: {self.player.Position}"
        self.stop()
        

    @discord.ui.button(label="Pass")
    async def Pass(self, interaction: discord.Interaction, _):
        await interaction.response.defer()
        await self.wait()
        self.result = f'{self.player.name} has `Passed`'
        self.stop()


class Attack(discord.ui.View):
    """Called when the player has chosen what type of attack they want to use.
    
    Shows what the ability they chose does, then makes them decide whether to use it or not.

    Parameters
    ---
    view :class:`discord.ui.View`
        Used to go back after player presses any button
    move :class:`str`
        The the name of the ability that player's going to use
    cPlayer :class:`Player`
        The player that is attacking
    players :class: `list[Player]`
        The players list
    """

    result: res.EResult
    __messages: list[discord.Message] = []

    def __init__(self,
        view: VAbilities | MoveChoice,
        move: core.Ability,
        cPlayer: Player,
        players: list[Player],
    ):
        
        super().__init__(timeout=None)
        self.previous = view
        self.lobby = players
        
        self.embed = discord.Embed(title=move, description=cPlayer.Weapon.Name, color=cPlayer.color)
        self.embed.set_image(url=cPlayer.Weapon.Image)
        self.embed.add_field(name='Description', value=move.long)

    @property
    def children(self) -> list[discord.ui.Button]:
        return super().children # type: ignore
    
    async def wait_for_players(self):
        await self.wait_players()
        for player in self.lobby:
            await player.wait()
        await self.stop_waiting()

    async def wait_players(self):
        for player in self.lobby:
            self.__messages.append(await player.send('Waiting for other players...'))

    async def stop_waiting(self):
        for message in self.__messages:
            await message.delete()
        self.__messages = []


    @discord.ui.button(label="Attack")
    async def Attack(self, interaction: discord.Interaction, _):
        self.result = res.EResult.Done
        await interaction.response.defer()
        await self.wait_for_players()
        await interaction.followup.edit_message(interaction.message.id, embed=self.previous.embed, view=self.previous) # type: ignore
        self.stop()

    @discord.ui.button(label="Back")
    async def Back(self, interaction: discord.Interaction, _):
        self.result = res.EResult.Back
        await interaction.response.defer()
        await self.wait_for_players()
        await interaction.followup.edit_message(interaction.message.id, embed=self.previous.embed, view=self.previous) # type: ignore
        self.stop()