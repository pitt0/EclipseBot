from typing import TYPE_CHECKING
from discord.ext import commands

import discord
import game
import views as choice

from game import Player

class Turn: pass

class Game:
    __slots__ = (
        'author',
        'players',
        'turn',
        'lobby',
        '_guild',
        '_channel'
    )

    if TYPE_CHECKING:
        author: Player
        players: list[Player]
        turn: Turn
        _guild: discord.Guild
        _channel: discord.TextChannel | None

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, self.__class__) and __o._guild.id == self._guild.id

    @property
    def id(self) -> int:
        return self._guild.id

    async def start(self) -> None:
        ...



class PvPGame(Game):
    def __init__(self, author, guild, lobby: list[Player]) -> None:
        self.author = author
        self.players = lobby
        self._guild = guild
        self._channel = None

    async def find_channel(self):
        for channel in self._guild.text_channels:
            if channel.name == 'eclipse-game':
                return channel

    async def ChangePlayersState(self, status: game.EActivity) -> None:
        for player in self.players:
            player.activity = status

    async def Teams(self):
        await self.ChangePlayersState(game.EActivity.ChoosingTeam)
        teams = choice.Teams(self.players)
        await self._channel.send()


    async def start(self, ctx: commands.Context):
        if not any(channel.name == 'eclipse-game' for channel in self._guild.text_channels):
            self._channel = await self._guild.create_text_channel('eclipse-game')
        else:
            self._channel = await self.find_channel()
            if self._channel is None:
                print('wtf')
                return

        await ctx.send(f'Game created at {self._channel.mention}')
        del ctx
        await self._channel.send()

        

class StoryGame(Game):
    pass

class MultiGuildPvPGame(Game):
    pass
