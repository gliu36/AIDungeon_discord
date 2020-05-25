import discord
from discord.ext import commands

from AIDungeon.generator.gpt2.gpt2_generator import *
from AIDungeon.story import grammars
from AIDungeon.story.story_manager import *
from AIDungeon.story.utils import *

class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('AI Script loaded')

    @commands.is_owner()
    async def play_dungeon(self, ctx, channel):
        await channel.send("Initializing AI Dungeon! (This might take a few minutes)")

        generator = GPT2Generator()
        story_manager = UnconstrainedStoryManager(generator)

        with open(r"AIDungeon/opening.txt", "r", encoding="utf-8") as f:
            starter = f.read()
        await channel.send(starter)


def setup(bot):
    bot.add_cog(AI(bot))