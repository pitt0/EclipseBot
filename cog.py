from discord.ext import commands
from dataclasses import dataclass

import discord
import random

from core import Player
from game.games import PvPGame
from views import *
import core
import game.abc as abc





class Game(commands.Cog):
    # TODO: remove the cog, may switch to slash commands

    game_instances: dict[int, abc.Game] = {}
 
    def __init__(self, bot: commands.Bot):

        super().__init__()
        self.bot = bot

    async def CurrentPlayerTurn(self, turn: Turn, player: Player) -> MoveChoice:
        move = MoveChoice(player, self.players, turn.prob, turn.buff)
        self.messages.append(await player.send(embed=move.embed, view=move))
        return move
    
    async def PlayerWaiting(self, turn: Turn, player: Player, cPlayer: Player):
        view = WaitingField(player, self.players, cPlayer, turn.prob, turn.buff)
        self.messages.append(await player.send(embed=view.embed, view=view))

    async def GeneralTurn(self, turn: Turn, cPlayer: Player):
        move = await self.CurrentPlayerTurn(turn, cPlayer)

        for player in self.players:
            if player == cPlayer:
                continue
            await self.PlayerWaiting(turn, player, cPlayer)

        await move.wait()
        return move

    async def TurnRecap(self, turn: Turn, result: str):

        shadows = [shadow for shadow in self.players if shadow.team is core.ETeam.Shadow]
        nobles = [noble for noble in self.players if noble.team is core.ETeam.Noble]

        embed = discord.Embed(
            title=f'Turn {turn} • Attack Result',
            description=result,
            color=discord.Color.blue()
        )
        if any(not player.Alive for player in self.players):
            embed.add_field(
                name='Dead Shadows', 
                value=''.join(f'{shadow.name}\n' for shadow in shadows if not shadow.Alive) if any(not shadow.Alive for shadow in shadows) else '-', 
                inline=True)
            embed.add_field(
                name='Dead Nobles', 
                value=''.join(f'{noble.name}\n' for noble in nobles if not noble.Alive) if any(not noble.Alive for noble in nobles) else '-', 
                inline=True)

        return embed

    def CheckTeams(self):
        nobles = [noble for noble in self.players if noble.team is core.ETeam.Noble]
        shadows = [shadow for shadow in self.players if shadow.team is core.ETeam.Shadow]
        return all(not player.Alive for player in shadows) or all(not player.Alive for player in nobles)

    async def EndGame(self):
        winners = 'Shadows' if any(shadow.Alive for shadow in self.players if shadow.team is core.ETeam.Shadow) else 'Nobles'
        for player in self.players:
            await player.send(f"Game ended\n{winners} win.")
        await self.destroy_game(f'{winners} win')

    async def destroy_game(self, reason: str) -> None:
        print(reason)
        self.in_game = False

    @commands.command(name='game')
    async def start_game(self, ctx: commands.Context):
        if ctx.guild is None:
            return
        
        if ctx.guild.id in self.game_instances:
            await ctx.send('A game is already running')
            return

        self.game_instances[ctx.guild.id] = PvPGame(ctx)
        try:
            await self.game_instances[ctx.guild.id].start()
        except Exception as e:
            print("Game has ended")
            print(e)
            return               
        

    @commands.command(name='restart')
    async def restart(self, ctx: commands.Context):
        await self.destroy_game('Restarted')


async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))