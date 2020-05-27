import discord
import json
from datetime import datetime
import os
from discord.ext import commands

bot = commands.Bot(command_prefix='>>')

extensions = [
    'cogs.server',
    'cogs.ai'
]

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('AI Dungeon 2'))

@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.CheckFailure): 
        await ctx.send("```Invalid command```")

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("```Exiting...```")
    await ctx.bot.logout()


# @bot.command()
# async def load(ctx, extension):
#     bot.load_extension(f'cogs.{extension}')

# @bot.command()
# async def unload(ctx, extension):
#     bot.unload_extension(f'cogs.{extension}')


def load_creds():
    with open('config.json') as f:
        return json.load(f)

if __name__ == '__main__':

    for ext in extensions:
        try:
            bot.load_extension(ext)
        except Exception as err:
            print(f'{ext} cannot be loaded. ({err})')

    creds = load_creds()
    bot.starttime = datetime.now()
    bot.run(creds['TOKEN'])