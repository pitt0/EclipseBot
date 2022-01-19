from discord.ext import commands

import discord
import datetime
import random
import pytz

from resources import *


class Lobby(discord.ui.View):
    """The discord View from where people can join a game.
    
    Parameter
    ---
    player :class:`discord.User | discord.Member`
        The person who requested to play.
    """


    def __init__(self, player: discord.User | discord.Member, bot: commands.Bot):
        super().__init__()
        self.players: list[discord.User] = [player]
        self.bot = bot
        
        embed = discord.Embed(title='Lobby', color=discord.Color.from_rgb(3, 97, 178))
        embed.add_field(name='Player 1', value=player.mention, inline=False)
        embed.set_footer(text=datetime.datetime.now(tz=pytz.timezone('Europe/Rome')).strftime('%A, %H:%M:%S'))
        self.embed = embed

        self.response: discord.Message = None
    
    async def update_embed(self) -> None:
        self.embed = await edit_embed(
            embed=self.embed,
            title='Lobby',
            colour=[3, 97, 178],
            fields={f'Player{x+1}': [player.mention, False] for x, player in enumerate(self.players)},
            )
        self.check_ready()

    def check_ready(self):
        children: list[discord.Button] = self.children
        if len(self.players) >= 2:
            children[-1].disabled = False
        else:
            children[-1].disabled = True 

    @discord.ui.button(label='Join', disabled=False)
    async def Join(self, button: discord.Button, interaction: discord.Interaction):
        if interaction.user in self.players:
            await interaction.response.send_message("You are already in the lobby", ephemeral=True)
            return
         
        self.players.append(interaction.user)

        if len(self.players) == 10:
            button.disabled = True

        await self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)


    @discord.ui.button(label='Exit')
    async def Exit(self, button: discord.Button, interaction: discord.Interaction):
        if interaction.user not in self.players:
            await interaction.response.send_message("You are not in the lobby", ephemeral=True)
            return

        self.players.remove(interaction.user)
        if not self.players:
            await interaction.message.delete()
            self.stop()
            return
        
        await self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='Add Bot')
    async def _add_bot(self, button: discord.Button, interaction: discord.Interaction):
        if interaction.user not in self.players:
            await interaction.response.send_message("You are not in the lobby", ephemeral=True)
            return

        self.players.append(random.choice([usr for usr in self.bot.get_all_members() if usr.bot]))

        if len(self.players) == 10:
            button.disabled = True

        await self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='Ready', disabled=True)
    async def Ready(self, button: discord.Button, interaction: discord.Interaction):
        if interaction.user not in self.players:
            await interaction.response.send_message("You are not in the lobby", ephemeral=True)
            return
        self.stop()

    async def on_timeout(self) -> None:
        children: list[discord.Button] = self.children
        for child in children:
            child.disabled = True
        self.players = {}
        await self.response.edit(view=self)
        self.stop()