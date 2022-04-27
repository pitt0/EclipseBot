from discord.ext import commands

import core
from . import abc # from `here` import `module`
import views as choice



class PvPGame(abc.InGuildGame):

    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(ctx)

    async def start(self) -> None:
        print(f'Game created in {self._guild.name}')
        await self.init_lobby()
        await self.team_choice()

        for player in self.players:
            await player.send(embed=self.teams)
            player.activity = core.EActivity.ChoosingWeapon

        await self.shop()
        await self._channel.send()

    async def fight(self) -> None:

        turn = abc.Turn() # should not be in super().fight()
        self.players.sort(key=lambda p: p.Speed) # should be in super().fight()

        while (
            any(player.Alive for player in self.players if player.team is core.ETeam.Shadow) 
            and 
            any(player.Alive for player in self.players if player.team is core.ETeam.Noble)
        ):

            # A turn passes when all the players have done their move
            turn.change()

            # Start of Turn
            for current_player in self.players:

                if not current_player.Alive:
                    continue

                move = await self.init_turn(turn, current_player)
                current_player.AfterAttack()

                for message in self.messages:
                    await message.delete()

                embed = await self.TurnRecap(turn, move.result)
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

        

class StoryGame(abc.InGuildGame):
    
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(ctx)

class MultiGuildPvPGame(abc.Game):
    pass
