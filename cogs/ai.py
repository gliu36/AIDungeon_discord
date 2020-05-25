import discord
from discord.ext import commands

class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('ni hao2')

    @commands.command()
    async def test_1(self, ctx, arg):
        await ctx.send(arg)

    @commands.command()
    async def clear_1(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)
        await ctx.send("Cleared {} messages.".format(amount))


def setup(bot):
    bot.add_cog(AI(bot))