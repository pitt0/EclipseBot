from discord.ext import commands

import discord
import core
import views as choice

from core import Player
from game import Game


class Turn: pass



class InGuildGame(Game):

    author: Player
    _guild: discord.Guild
    _channel: discord.TextChannel

    def __init__(self, ctx: commands.Context) -> None:
        
        self.author = ctx.author # type: ignore
        self._guild = ctx.guild # type: ignore
        self._channel = ctx.channel # type: ignore


class PvPGame(InGuildGame):

    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(ctx)

    async def Teams(self):
        await self.change_players_state(core.EActivity.ChoosingTeam)
        teams = choice.Teams(self.players)
        await self._channel.send()

    async def start(self):
        print(f'Game created in {self._guild.name}')

        await self._channel.send()

        

class StoryGame(InGuildGame):
    
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(ctx)

class MultiGuildPvPGame(Game):
    pass
