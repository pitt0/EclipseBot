from dotenv import load_dotenv
from discord.ext import commands

import discord
import os
import datetime
import pytz

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    help_command=None,
    intents=discord.Intents.all()
)

@bot.event
async def on_ready():
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Rome'))
    print(f"[{now.strftime('%H:%M:%S')}] Bot started.")


if __name__ == '__main__':
    load_dotenv('./secrets/.env')
    bot.load_extension('cog')
    bot.run(os.getenv('TOKEN'))