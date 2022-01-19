from discord.ext import commands
from dataclasses import dataclass

import discord
import random

from game import Player
from views import *
from resources import EBuff, Buff
import game


@dataclass
class Turn:
    prob: bool
    buff: Buff
    _turn: int = 0

    def Pass(self, prob: bool, buff: Buff):
        self.prob = prob
        self.buff = buff
        self._turn += 1

    def __repr__(self) -> str:
        return str(self._turn)


class GameEnded(BaseException):
    """Raised whenever the game ends"""

class Game(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot
        self.inGame: bool = False
        self.players: list[Player] = []
        self.turn = Turn()
        self.messages: list[discord.Message] = []

    @commands.Cog.listener()
    async def on_command_error(self, error: Exception):

        self.inGame = False
        raise error

    async def lobby(self, ctx: commands.Context):
        
        lobby = Lobby(ctx.author)
        t = await ctx.send(embed=lobby.embed, view=lobby)
        lobby.response = t

        await lobby.wait()

        await t.delete()
        return lobby.players

    async def teams(self, ctx: commands.Context):

        for player in self.players:
            player.activity = game.EActivity.ChoosingTeam

        teams = Teams(self.players)
        t = await ctx.send(embed=teams.embed, view=teams)
        teams.response = t

        await teams.wait()

        await t.delete()
        return teams.players

    async def shop(self):
        
        shops: list[Shop] = []
        
        for player in self.players:

            player.activity = game.EActivity.ChoosingWeapon
            await player.send(embed=self.team_embed)
            
            shop = Shop(player)
            shops.append(shop)
            msg = await player.send(embed=shop.embed, view=shop)
            shop.message = msg

        for shop in shops:
            await shop.wait()
        for shop in shops:
            await shop.message.delete()

        for shop in shops:
            index = self.players.index(shop.player) # Player's __eq__ works also with subclasses of, and searches by discord.User
            self.players[index] = shop.player

            del shop
        
    @property
    def team_embed(self) -> discord.Embed:

        shadows = [player for player in self.players if player.team is game.ETeam.Shadow]
        nobles = [player for player in self.players if player.team is game.ETeam.Noble]

        embed = discord.Embed(title='Teams', color=discord.Colour.purple())
        embed.add_field(name='Shadows', value='\n'.join(player.mention for player in shadows))
        
        if len(shadows) > len(nobles): length = len(shadows)
        else: length = len(nobles)
        
        embed.add_field(name='-', value='\n'.join('-' for _ in range(length)))

        embed.add_field(name='Nobles', value='\n'.join(player.mention for player in nobles))

        return embed

    async def CurrentPlayerTurn(self, player: Player) -> Move:
        move = Move(player, self.players, self.turn.prob, self.turn.buff)
        self.messages.append(await player.send(embed=move.embed, view=move))
        return move
    
    async def PlayerWaiting(self, player: Player, cPlayer: Player):
        view = WaitingField(player, self.players, cPlayer, self.turn.prob, self.turn.buff)
        self.messages.append(await player.send(embed=view.embed, view=view))

    async def GeneralTurn(self, cPlayer: Player):
        move = await self.CurrentPlayerTurn(cPlayer)

        for player in self.players:
            if player == cPlayer:
                continue
            await self.PlayerWaiting(player, cPlayer)

        await move.wait()
        return move

    async def TurnRecap(self, result: str):

        shadows = [shadow for shadow in self.players if shadow.team is game.ETeam.Shadow]
        nobles = [noble for noble in self.players if noble.team is game.ETeam.Noble]

        embed = discord.Embed(
            title=f'Turn {self.turn} • Attack Result',
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
        nobles = [noble for noble in self.players if noble.team is game.ETeam.Noble]
        shadows = [shadow for shadow in self.players if shadow.team is game.ETeam.Shadow]
        return all(not player.Alive for player in shadows) or all(not player.Alive for player in nobles)

    async def EndGame(self):
        winners = 'Shadows' if any(shadow.Alive for shadow in self.players if shadow.team is game.ETeam.Shadow) else 'Nobles'
        for player in self.players:
            await player.send(f"Game ended\n{winners} win.")
        raise GameEnded(f'{winners} win')

    @commands.command(name='game')
    async def start_game(self, ctx: commands.Context):
        
        await ctx.message.delete()
        if self.inGame:
            await ctx.send('A game instance is already running')
            return

        self.inGame = True

        # Lobby
        players = await self.lobby(ctx)
        if len(players) in (0, 1) or all(usr.bot for usr in players):
            raise GameEnded('Game has ended at lobby')

        self.players = [Player(user) for user in players]
        
        # Team Choice
        players = await self.teams(ctx)
        if any(player.team is None for player in self.players):
            raise GameEnded('Game has ended at team selection.')

        self.players = players

        # Weapon Choice
        await self.shop()

        
        # Fight
        while (
            any(player.Alive for player in self.players if player.team is game.ETeam.Shadow) 
            and 
            any(player.Alive for player in self.players if player.team is game.ETeam.Noble)
        ):
            
            self.players.sort(key=lambda p: p.Speed)

            # A turn passes when all the players have done their move
            prob = random.randint(0, 100)
            buff = Buff(
                random.randint(0, 4),
                random.randint(0, 3),
                random.choice(EBuff.mro())
            )
            self.turn.Pass(prob, buff)            

            # Start of InnerTurn
            for cPlayer in self.players:

                if not cPlayer.Alive:
                    continue

                move = await self.GeneralTurn(cPlayer)
                cPlayer.AfterAttack()

                for message in self.messages:
                    await message.delete()

                embed = await self.TurnRecap(move.result)
                for player in self.players:
                    await player.send(embed=embed)

                if self.CheckTeams():
                    await self.EndGame()

            # End Turn
            for player in self.players:
                log = player.EndTurn()
                if log:
                    for player in self.players:
                        await player.send(log)
                
                if self.CheckTeams():
                    await self.EndGame()
        
        await self.EndGame()


def setup(bot: commands.Bot):
    bot.add_cog(Game(bot))