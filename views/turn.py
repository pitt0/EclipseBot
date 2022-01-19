from typing import Any

import discord

from game import Player
import resources as res
from .field import *

__all__ = (
    'Ability', 
    'Move',
    'Attack'
)


class Ability(discord.ui.Button["Abilities"]):
    """Represents an ability Button
    Parameters
    ---
    ability :class:`str`
        The ability name
    stamina :class:`bool`
        Whether the ability is clickable or not, bool will be used on button.disabled
    """
    def __init__(self, ability: str, stamina: bool):
        super().__init__(label=ability, row=0, disabled=stamina)

    async def callback(self, interaction: discord.Interaction):

        ability: dict[str, Any] = self.view.player.Abilities[self.label]
        
        attack = Attack(self.view, self.label, self.view.player, self.view.players, res.EAttackType.Ability)
        await interaction.response.edit_message(embed=attack.embed, view=attack)
        await attack.wait()

        if not attack.attack: # If player pressed 'Back'
            return

        allies = [player for player in self.view.players if player.team == self.view.player.team and player != self.view.player and player.Alive]
        match ability.get('Targets', 1):
            case -2:
                targets = [enemy for enemy in self.view.enemies if enemy.cHealth < enemy.Health]
                self.view.result = ability['Callable'](targets, allies)
            case -1:
                self.view.result = ability['Callable'](self.view.enemies, allies)
            case 0:
                self.view.result = ability['Callable'](None, allies)
            case _:
                targets: list[Player] = []
                while len(targets) < ability.get('Targets', 1):
                    field = FightField(self.view.player, self.view.players, targets)
                    await interaction.message.edit(embed=field.embed, view=field)
                    await field.wait()
                    match field.target:
                        case res.ETarget.Back:
                            try:
                                targets.pop(-1)
                                continue
                            except IndexError:
                                await interaction.message.edit(embed=self.view.previous.embed, view=self.view.previous)
                                self.view.stop()
                                return
                        case res.ETarget.Done:
                            if len(targets) == 0:
                                continue
                            break
                        case _:
                            targets.append(field.target)
                
                if ability.get('Targets', 1) == 1:
                    self.view.result = ability['Callable'](targets[0], allies)
                else:
                    self.view.result = ability['Callable'](targets, allies)

        await self.view.wait_for_players()
        self.view.stop()


class Abilities(discord.ui.View):
    """A wrapper for player's abilities"""

    def __init__(
        self,
        previous_view: 'Move',
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
        disabled = False
        for ability in abilities:
            match player.Weapon.Name:
                case 'Sharpened Katana':
                    print(player.Weapon.UsedAbilities)
                    if ability in player.Weapon.UsedAbilities:
                        disabled = True
                    self.embed.set_footer(text='A disabled button means that you have no enouhg stamina or you already used this ability.\nYou must use all the ability once before you can use one twice.')
                case "Shadows's Dagger":
                    disabled = self.player.cHealth <= round(abilities[ability]['Health'])
                case 'Reaper Bow':
                    disabled = False
                case _:
                    disabled = self.player.cStamina < abilities[ability].get('Stamina', 0)
            self.add_item(Ability(ability, disabled))

        self.allies = allies
        self.enemies = enemies
        self.players = players

        self.result: str = None

    @discord.ui.button(label='<<')
    async def back_btn(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.previous.embed, view=self.previous)
        self.stop()

    async def enable_buttons(self, disable: bool = False):
        children: list[discord.Button] = self.children
        for child in children:
            child.disabled = disable

    async def wait_for_players(self):
        await self.wait_players()
        for player in self.players:
            await player.wait_ready()
        await self.stop_waiting()

    async def wait_players(self):
        await self.enable_buttons(disable=True)
        for player in self.players:
            self.user_messages.append(await player.send('Waiting for other players...'))

    async def stop_waiting(self):        
        await self.enable_buttons(disable=False)
        for message in self.user_messages:
            await message.delete()
        self.user_messages = []


class Move(discord.ui.View):
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

    def __init__(self, player: Player, players: list[Player], prob: int, buff: res.Buff):
        super().__init__(timeout=None)
        self.player = player
        self.allies = [pl for pl in players if pl.team == player.team and player != pl]
        self.enemies = [pl for pl in players if pl.team != player.team]
        self.lobby = players
        
        self.prob = prob
        self.buff = buff

        self.user_messages: list[discord.Message] = []

        self.embed = discord.Embed(title='Your Turn', description='Make your choice', color=player.color)
        self.embed.add_field(name='Base Attack', value=player.Weapon.BA, inline=False)
        for ability in player.Abilities:
            self.embed.add_field(name=ability, value=player.Abilities[ability]['Brief'], inline=False)

        self.result: str = None

    async def enable_buttons(self, disable: bool = False):
        children: list[discord.Button] = self.children
        for child in children:
            child.disabled = disable

    async def wait_for_players(self):
        await self.wait_players()
        for player in self.lobby:
            await player.wait_ready()
        await self.stop_waiting()

    async def wait_players(self):
        await self.enable_buttons(disable=True)
        for player in self.lobby:
            self.user_messages.append(await player.send('Waiting for other players...'))

    async def stop_waiting(self):        
        await self.enable_buttons(disable=False)
        for message in self.user_messages:
            await message.delete()
        self.user_messages = []

    @discord.ui.button(label="Base Attack")
    async def BaseAttack(self, button: discord.Button, interaction: discord.Interaction):
    
        await interaction.response.defer()
        await self.wait_for_players()

        attack = Attack(self, 'Base Attack', self.player, self.lobby, res.EAttackType.BaseAttack)
        await interaction.followup.edit_message(interaction.message.id, embed=attack.embed, view=attack)
        await attack.wait()
        await self.wait_for_players()

        if not attack.attack: # If user pressed 'Back'
            return

        
        field = FightField(self.player, self.lobby, [], self.prob, self.buff)
        await interaction.followup.edit_message(interaction.message.id, embed=field.embed, view=field)
        await field.wait()
        await self.wait_for_players()

        self.result = self.player.BaseAttack(field.target)
        
        self.stop()
        
    @discord.ui.button(label="Ability")
    async def Ability(self, button: discord.Button, interaction: discord.Interaction):
        abilities = Abilities(self, self.player, self.allies, self.enemies, self.lobby)
        await interaction.response.edit_message(embed=abilities.embed, view=abilities)
        await abilities.wait()
        if abilities.result is None:
            return

        self.result = abilities.result
        self.stop()

    @discord.ui.button(label='Move')
    async def Move(self, button: discord.Button, interaction: discord.Interaction):

        await interaction.response.defer()
        await self.wait_for_players()
        
        field = MovingField(self.player, self.lobby, self.prob, self.buff)
        await interaction.followup.edit_message(embed=field.embed, view=field)
        await field.wait()
        if field.result == res.ETarget.Back:
            return 

        await self.wait_for_players()
        self.result = f"{self.player.name} moved to position: {', '.join(self.player.Position)}"
        self.stop()
        

    @discord.ui.button(label="Pass")
    async def Pass(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.wait_for_players()
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
    attack_type :enum:`EAttackType`
        The type of attack user chose is.
    """

    def __init__(self,
        view: Ability | Move,
        move: str,
        cPlayer: Player,
        players: list[Player],
        attack_type: res.EAttackType
    ):
        
        super().__init__(timeout=None)
        self.previous = view
        self.move = move
        self.player = cPlayer
        self.lobby = players

        self.attack: bool = False
        self.user_messages: list[discord.Message] = []

        match attack_type:
            case res.EAttackType.BaseAttack:
                desc = cPlayer.Weapon.BA
            case res.EAttackType.Ability:
                desc = cPlayer.Abilities[move]['Description']
        
        self.embed = discord.Embed(title=move, description=cPlayer.Weapon.Name, color=cPlayer.color)
        self.embed.set_image(url=cPlayer.Weapon.Image)
        self.embed.add_field(name='Description', value=desc)
    
    async def enable_buttons(self, disable: bool = False):
        children: list[discord.Button] = self.children
        for child in children:
            child.disabled = disable

    async def wait_for_players(self):
        await self.wait_players()
        for player in self.lobby:
            await player.wait_ready()
        await self.stop_waiting()

    async def wait_players(self):
        for player in self.lobby:
            self.user_messages.append(await player.send('Waiting for other players...'))

    async def stop_waiting(self):
        for message in self.user_messages:
            await message.delete()
        self.user_messages = []


    @discord.ui.button(label="Attack")
    async def Attack(self, button: discord.Button, interaction: discord.Interaction):
        self.attack = True
        await interaction.response.defer()
        await self.wait_for_players()
        await interaction.followup.edit_message(interaction.message.id, embed=self.previous.embed, view=self.previous)
        self.stop()

    @discord.ui.button(label="Back")
    async def Back(self, button: discord.Button, interaction: discord.Interaction):
        self.attack = False
        await interaction.response.defer()
        await self.wait_for_players()
        await interaction.followup.edit_message(interaction.message.id, embed=self.previous.embed, view=self.previous)
        self.stop()