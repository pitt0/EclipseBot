from dotenv import load_dotenv
from discord.ext import commands

import discord
import os
import datetime
import pytz

from game import PvPGame, Game


game_instances: dict[int, Game] = {}

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    help_command=None,
    intents=discord.Intents.all()
)


@bot.event
async def on_ready():
    await bot.load_extension('cog')
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Rome'))
    print(f"[{now.strftime('%H:%M:%S')}] Bot started.")


@bot.command()
async def start_game(ctx: commands.Context):
    if ctx.guild is None:
        return
    
    if ctx.guild.id in game_instances:
        await ctx.send('A game is already running')
        return

    game_instances[ctx.guild.id] = PvPGame(ctx)
    try:
        await game_instances[ctx.guild.id].start()
    except Exception as e:
        del game_instances[ctx.guild.id]
        print(e)
        return


if __name__ == '__main__':
    load_dotenv('./secrets/.env')
    bot.run(os.getenv('TOKEN'))