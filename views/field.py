import discord
import random

import resources as res
from game import Player
import game
from .info import Info


__all__ = (
    'WaitingField',
    'FightField',
    'MovingField'
)


class FightFieldButton(discord.ui.Button["FightField"]):
    def __init__(
        self, 
        player: Player | None = None, 
        label: str = '\u200b', 
        row: int = 0, 
        disabled: bool = False, 
        style: discord.ButtonStyle = discord.ButtonStyle.grey
    ):

        self.player = player
        super().__init__(label=label, disabled=disabled or (not player), row=row, style=style)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.player: # If user clicked 'You'
            self.view.target = self.player
            self.view.stop()
            return

        await self.view.enable_buttons(disabled=True)
        self.player.activity = game.EActivity.WatchingInfo
        info = Info(self.player)
        await interaction.response.send_message(embed=info.embed, view=info)
        await info.wait()
        await self.view.enable_buttons(disabled=False)

class FightField(discord.ui.View):
    """Represents the field of the current player.
    """
    def __init__(self,
        player: Player,
        players: list[Player],
        targets: list[Player],
        prob: int,
        buff: res.Buff
    ):

        super().__init__(timeout=None)
        _placed: dict[tuple[int, int], Player] = {}
    
        self.target: Player = None
        
        self.embed = discord.Embed(
            title='Field',
            description='Choose your target',
            color=player.color
        )
        for _player in players:
            if not _player.Alive:
                continue
            if _player.Position is None:
                pCoordinates = _player.Coordinates(_placed, 'as_enemy' if _player.team == player.team else 'as_player')
                _player.Position = pCoordinates

            _placed[_player.Position] = _player
        
        if prob <= 25 and len(_placed) < 10:
            for i in range(4):
                if (buff.x + i, buff.y) not in _placed:
                    buff.x += i
                    break
                if (buff.x, buff.y + i) not in _placed:
                    buff.y += i
                    break
                if (buff.x - i, buff.y) not in _placed:
                    buff.x -= i
                    break
                if (buff.x, buff.y - i) not in _placed:
                    buff.y -= i
                    break

        print(_placed)

        for x in range(5):
            for y in range(4):
                
                if not _placed.get((x, y)):
                    if prob <= 25 and (x, y) == (buff.x, buff.y):
                        match buff.buff:
                            case res.EBuff.Health:
                                label = 'Hp +50'
                            case res.EBuff.Stamina:
                                label = 'St +25'
                            case res.EBuff.Strength | res.EBuff.Intelligence:
                                label = f'{buff.buff.name[:2]} +25'
                            case res.EBuff.Armor | res.EBuff.Perception:
                                label = f'{buff.buff.name[:2]} +15'
                        
                        self.add_item(FightFieldButton(label=label, row=y, disabled=True))
                        continue

                    self.add_item(FightFieldButton(row=y, disabled=True))
                    continue
                
                p = _placed[(x, y)]
                if p == player:
                    label = 'You'

                else:
                    label = p.name[0]

                if p.cHealth >= p.Health * 0.75:
                    style = discord.ButtonStyle.green
                elif p.cHealth <= p.Health * 0.25:
                    style = discord.ButtonStyle.red
                else:
                    style = discord.ButtonStyle.grey

                self.add_item(FightFieldButton(p, label, row=y, disabled=p in targets, style=style))


    async def enable_buttons(self, disabled=False):
        children: list[FieldButton] = self.children
        for child in children:
            child.disabled = disabled

    @discord.ui.button(label='Back', row=4)
    async def back_btn(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        self.target = res.ETarget.Back
        self.stop()
    
    @discord.ui.button(label='Attack', row=4)
    async def done_btn(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        self.target = res.ETarget.Done
        self.stop()


class MovingFieldButton(discord.ui.Button['MovingField']):

    def __init__(self, 
        label: str = '\u200b',
        disabled: bool = False, 
        row: int = 0, 
        style: discord.ButtonStyle = discord.ButtonStyle.grey,
        buff: res.Buff = None
    ):
        if buff:
            style = discord.ButtonStyle.grey
            match buff.buff:
                case res.EBuff.Health:
                    label = 'Hp +50'
                case res.EBuff.Stamina:
                    label = 'St +25'
                case res.EBuff.Strength | res.EBuff.Intelligence:
                    label = f'{buff.buff.name[:2]} +25'
                case res.EBuff.Armor | res.EBuff.Perception:
                    label = f'{buff.buff.name[:2]} +15'
        else:
            label = '\u200b'
        self.buff = buff
        super().__init__(label=label, disabled=disabled, row=row, style=style)

    async def callback(self, interaction: discord.Interaction):
        self.view.player.Position = (self.buff.x, self.buff.y)
        match self.buff.buff:
            case res.EBuff.Strength:
                self.view.player.Strength += 25
            case res.EBuff.Armor:
                self.view.player.Armor += 15
            case res.EBuff.Intelligence:
                self.view.player.Intelligence += 25
            case res.EBuff.Perception:
                self.view.player.Perception += 15
            case res.EBuff.Health:
                self.view.player.cHealth += 50
            case res.EBuff.Stamina:
                self.view.player.cStamina += 25
        await interaction.response.edit_message(embed=self.view.embed, view=self.view)
        self.stop()

class MovingField(discord.ui.View):

    def __init__(self,
        player: Player,
        players: list[Player],
        prob: int,
        buff: res.Buff
    ):

        super().__init__(timeout=None)
        _placed: dict[tuple[int, int], Player] = {}
        
        self.player = player
        self.result = res.ETarget.Moved

        self.buff = buff
        
        self.embed = discord.Embed(
            title='Field',
            description='Move to postion',
            color=player.color
        )
        for _player in players:
            if not _player.Alive:
                continue
            if _player.Position is None:
                pCoordinates = _player.Coordinates(_placed, 'as_enemy' if _player.team == player.team else 'as_player')
                _player.Position = pCoordinates

            _placed[_player.Position] = _player

        if prob <= 25 and len(_placed) < 10:
            for i in range(4):
                if (buff.x + i, buff.y) not in _placed:
                    buff.x += i
                    break
                if (buff.x, buff.y + i) not in _placed:
                    buff.y += i
                    break
                if (buff.x - i, buff.y) not in _placed:
                    buff.x -= i
                    break
                if (buff.x, buff.y - i) not in _placed:
                    buff.y -= i
                    break

        print(_placed)

        for x in range(5):
            for y in range(4):
                
                if not _placed.get((x, y)):
                    if prob <= 25:
                        if x == self.buff.x and y == self.buff.y:
                            self.add_item(MovingFieldButton(x=x, row=y, buff=self.buff))
                    self.add_item(MovingFieldButton(x=x, row=y))
                    continue
                
                p = _placed[(x, y)]
                if p == player:
                    label = 'You'

                elif p in players:
                    label = p.name[0]
                
                else:
                    label = '\u200b'

                if p.cHealth >= p.Health * 0.75:
                    style = discord.ButtonStyle.green
                elif p.cHealth <= p.Health * 0.25:
                    style = discord.ButtonStyle.red
                else:
                    style = discord.ButtonStyle.grey

                self.add_item(MovingFieldButton(label, x, row=y, disabled=True, style=style))

    @discord.ui.button(label='Back', row=4)
    async def back_btn(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        self.target = res.ETarget.Back
        self.stop()


class FieldButton(discord.ui.Button['WaitingField']):

    def __init__(self, player: Player| None = None, label: str = '\u200b', row: int = 0, style: discord.ButtonStyle = discord.ButtonStyle.grey):

        self.player = player
        super().__init__(label=label, disabled=(not player), row=row, style=style)

    async def callback(self, interaction: discord.Interaction):
        info = Info(self.player)
        await self.view.enable_buttons(disabled=True)
        self.player.activity = game.EActivity.WatchingInfo
        await interaction.response.send_message(embed=info.embed, view=info)
        await info.wait()
        await self.view.enable_buttons()


class WaitingField(discord.ui.View):

    def __init__(self,
        player: Player,
        players: list[Player],
        current_player: Player,
        prob: int,
        buff: res.Buff
    ):

        super().__init__(timeout=None)
        _placed: dict[tuple[int, int], Player] = {}
    
        self.embed = discord.Embed(title='Field', description=f'Waiting for {current_player.mention}', color=player.color)
        self.embed.set_footer(text='If you click on any player you will see their info.')

        for _player in players:
            if not _player.Alive:
                continue
            if _player.Position is None:
                pCoordinates = _player.Coordinates(_placed, 'as_enemy' if _player.team == player.team else 'as_player')
                _player.Position = pCoordinates
            _placed[_player.Position] = _player

        if prob <= 25 and len(_placed) < 10:
            for i in range(4):
                if (buff.x + i, buff.y) not in _placed:
                    buff.x += i
                    break
                if (buff.x, buff.y + i) not in _placed:
                    buff.y += i
                    break
                if (buff.x - i, buff.y) not in _placed:
                    buff.x -= i
                    break
                if (buff.x, buff.y - i) not in _placed:
                    buff.y -= i
                    break

        print(_placed)
            
        for x in range(5):
            for y in range(4):
                
                if not _placed.get((x, y)):
                    if prob <= 25 and (x, y) == (buff.x, buff.y):
                        match buff.buff:
                            case res.EBuff.Health:
                                label = 'Hp +50'
                            case res.EBuff.Stamina:
                                label = 'St +25'
                            case res.EBuff.Strength | res.EBuff.Intelligence:
                                label = f'{buff.buff.name[:2]} +25'
                            case res.EBuff.Armor | res.EBuff.Perception:
                                label = f'{buff.buff.name[:2]} +15'
                        
                        self.add_item(FightFieldButton(label=label, row=y, disabled=True))
                        continue
                    self.add_item(FieldButton(row=y))
                    continue
                
                p = _placed[(x, y)]
                if p == player:
                    label = 'You'

                elif p in players:
                    label = p.name[0]

                else:
                    label = '\u200b'
                    
                if p.cHealth >= p.Health * 0.75:
                    style = discord.ButtonStyle.green
                elif p.cHealth <= p.Health * 0.25:
                    style = discord.ButtonStyle.red
                else:
                    style = discord.ButtonStyle.grey

                self.add_item(FieldButton(p, label, row=y, style=style))

    async def enable_buttons(self, disabled=False):
        children: list[FieldButton] = self.children
        for child in children:
            child.disabled = disabled