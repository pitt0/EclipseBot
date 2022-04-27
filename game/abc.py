from dataclasses import dataclass
from core import Player
from discord.ext import commands

import core
import discord
import random
import views as choice


class GameEnded(Exception):
    """Exception raised when the game ends"""


@dataclass
class Turn:
    prob: int = 0
    buff: core.Buff = None # type: ignore
    _turn: int = 0

    def change(self):
        self.prob = random.randint(0, 100)
        self.buff = core.Buff(
            core.Position(random.randint(0, 4), random.randint(0, 3)),
            random.choice(tuple(core.BuffStat._member_map_.values())) # type: ignore
        )
        self._turn += 1

    def __repr__(self) -> str:
        return str(self._turn)


class Game:
    __slots__ = ()

    players: list[Player]
    __messages: list[discord.Message]
    shadows: list[Player]
    nobles: list[Player]

    @property
    def teams(self) -> discord.Embed:
        print('debug')

        embed = discord.Embed(title='Teams', color=discord.Colour.purple())
        embed.add_field(name='Shadows', value='\n'.join(player.mention for player in self.shadows))
        
        if len(self.shadows) > len(self.nobles): length = len(self.shadows)
        else: length = len(self.nobles)
        
        embed.add_field(name='-', value='\n'.join('-' for _ in range(length)))

        embed.add_field(name='Nobles', value='\n'.join(player.mention for player in self.nobles))

        return embed

    async def turn_recap(self, turn: Turn, result: str) -> discord.Embed:
        embed = discord.Embed(
            title=f'Turn {turn} • Attack Result',
            description=result,
            color=discord.Color.blue()
        )
        if any(not player.Alive for player in self.players):
            embed.add_field(
                name='Dead Shadows', 
                value=''.join(f'{shadow.name}\n' for shadow in self.shadows if not shadow.Alive) if any(not shadow.Alive for shadow in self.shadows) else '-', 
                inline=True)
            embed.add_field(
                name='Dead Nobles', 
                value=''.join(f'{noble.name}\n' for noble in self.nobles if not noble.Alive) if any(not noble.Alive for noble in self.nobles) else '-', 
                inline=True)

        return embed

    def check_teams(self) -> bool:
        return all(not player.Alive for player in self.shadows) or all(not player.Alive for player in self.nobles)

    async def start(self) -> None:
        ...

    async def change_players_state(self, status: core.EActivity) -> None:
        for player in self.players:
            player.activity = status

    async def end_game(self) -> None:
        winners = 'Shadows' if any(shadow.Alive for shadow in self.players if shadow.team is core.ETeam.Shadow) else 'Nobles'
        for player in self.players:
            await player.send(f"Game ended\n{winners} win.")
        raise GameEnded(f'{winners} win')

    async def init_lobby(self) -> None:
        ...

    async def fight(self) -> None:
        ...

    async def init_turn(self, turn: Turn, current: Player) -> choice.MoveChoice:
        self.__messages = []
        move = choice.MoveChoice(current, self.players, turn.prob, turn.buff)
        self.__messages.append(await current.send(embed=move.embed, view=move))

        for player in self.players:
            if player == current:
                continue
            view = choice.WaitingField(player, self.players, current, turn.prob, turn.buff)
            self.__messages.append(await player.send(embed=view.embed, view=view))

        await move.wait()
        return move

    async def delete_messages(self) -> None:
        for message in self.__messages:
            await message.delete()


class InGuildGame(Game):

    author: Player
    _guild: discord.Guild
    _channel: discord.TextChannel

    def __init__(self, ctx: commands.Context) -> None:
        
        self.author = ctx.author # type: ignore
        self._guild = ctx.guild # type: ignore
        self._channel = ctx.channel # type: ignore

    async def init_lobby(self) -> None:
        
        lobby = choice.Lobby(self.author)
        lobby.response = await self._channel.send(embed=lobby.embed, view=lobby)

        await lobby.wait()

        await lobby.response.delete()
        if len(lobby.players) <= 1:
            raise GameEnded("Game ended at lobby.")

        self.players = [Player(user) for user in lobby.players]

    async def team_choice(self) -> None:
        await self.change_players_state(core.EActivity.ChoosingTeam)
        teams = choice.Teams(self.players)
        _message = await self._channel.send(embed=teams.embed, view=teams)
        await teams.wait()

        await _message.delete()
        if any(player.team is None for player in teams.players):
            raise GameEnded("Someone has not chosen a team.")
        self.shadows = [player for player in self.players if player.team is core.ETeam.Shadow]
        self.nobles = [player for player in self.players if player.team is core.ETeam.Noble]

    async def shop(self) -> None:
        shops: list[choice.Shop] = []

        for player in self.players:
            shop = choice.Shop(player)
            shops.append(shop)
            shop.message = await player.send(embed=shop.embed, view=shop)

        for shop in shops:
            await shop.wait()
        for shop in shops:
            await shop.message.delete()

        for shop in shops:
            # Each player now has their own Character Class
            # we should update the list 
            index = self.players.index(shop.player) # Player's __eq__ also works with their subclasses, and searches by discord.User
            self.players[index] = shop.player

            del shop
        del shops