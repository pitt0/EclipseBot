from discord.ext import commands

from game import PvPGame, Game





class Game(commands.Cog):
    # TODO: remove the cog, may switch to slash commands

    game_instances: dict[int, Game] = {}
 
    def __init__(self, bot: commands.Bot):

        super().__init__()
        self.bot = bot

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
        

    # @commands.command(name='restart')
    # async def restart(self, ctx: commands.Context):
    #     await self.destroy_game('Restarted')


async def setup(bot: commands.Bot):
    await bot.add_cog(Game(bot))