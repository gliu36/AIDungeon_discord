import discord
from discord.ext import commands

class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('AI Script loaded')

    @commands.command()
    async def say_1(self, ctx, arg):
        await ctx.send(arg)


def setup(bot):
    bot.add_cog(AI(bot))