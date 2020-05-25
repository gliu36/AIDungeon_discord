import discord
from discord.ext import commands

class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('AI Script loaded')

    @commands.is_owner()
    async def start_dungeon(self, ctx, channel):
        await channel.send("Initializing AI Dungeon! (This might take a few minutes)")


def setup(bot):
    bot.add_cog(AI(bot))