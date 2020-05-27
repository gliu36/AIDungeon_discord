import discord
from discord.ext import commands

from AIDungeon.generator.gpt2.gpt2_generator import GPT2Generator
from AIDungeon.story.story_manager import UnconstrainedStoryManager

class Server(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Move this to json or server later
        self.dungeon_instances = {}

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Server script loaded')

    @commands.command()
    async def new_game(self, ctx):
        name = ctx.author.name
        _id = ctx.author.id

        # Only 1 instance per user
        if ctx.author.id in self.dungeon_instances.keys():
            await ctx.send(f"{ctx.author.mention} You already have a dungeon: {ctx.bot.get_channel(self.dungeon_instances[_id]['ROOM_ID']).mention}. Use '>>restart' to restart your dungeon.")
        else:
            guild = ctx.guild
            channel = await guild.create_text_channel(f"{name}_dungeon")
            self.dungeon_instances[ctx.author.id] = {}
            self.dungeon_instances[ctx.author.id]['ROOM_ID'] = channel.id
            await ctx.send(f"{ctx.author.mention} is now the dungeon master of {channel.mention}.")
            await self.set_permissions(ctx, channel)
            await self.create_dungeon(ctx, channel)


    async def set_permissions(self, ctx, channel):
        perms = discord.PermissionOverwrite()
        perms.read_messages = True
        perms.send_messages = False
        for member in ctx.guild.members:
            # For all other members excpet the bot and DM
            if ctx.author.id != ctx.bot.user.id and member != ctx.author:
                await channel.set_permissions(member, overwrite=perms)

    async def create_dungeon(self, ctx, channel):
        ai = self.bot.get_cog('AI')
        if ai is not None:
            # Lock channel
            perms = discord.PermissionOverwrite()
            perms.send_messages = False
            await channel.set_permissions(ctx.author, overwrite=perms)
            await channel.send("```Initializing AI Dungeon! (This might take a few minutes)```")

            # Create story
            generator = GPT2Generator()
            story_manager = UnconstrainedStoryManager(generator)

            self.dungeon_instances[ctx.author.id]['GENERATOR'] = generator
            self.dungeon_instances[ctx.author.id]['STORY'] = story_manager

            # Play with this story
            await ai.play_dungeon(ctx, channel, generator, story_manager)
        else:
            await channel.send("Something horribly wrong occured...")

    @commands.command()
    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"```Cleared {amount} messages```")

    @commands.command()
    async def my_dungeon(self, ctx):
        if ctx.author.id in self.dungeon_instances:
            await ctx.send(f"{ctx.author.mention} This is your dungeon {ctx.bot.get_channel(self.dungeon_instances[ctx.author.id]['ROOM_ID']).mention}")
        else:
            await ctx.send(f"{ctx.author.mention} You do not have a dungeon. Make one with >>new_game")

    @commands.command()
    async def restart(self, ctx):
        a = ctx.author
        if a.id in self.dungeon_instances:
            await ctx.bot.get_channel(self.dungeon_instances[a.id]['ROOM_ID']).delete()
            del self.dungeon_instances[a.id]
            await ctx.send(f"{ctx.author.mention} Your dungeon is cleared.")
        else:
            await ctx.send(f"{ctx.author.mention} You have no dungeon to clear.")

    @commands.command()
    @commands.is_owner()
    async def restart_all(self, ctx):
        if not self.dungeon_instances:
            await ctx.send(f"```No dungeons to reset.```")
        else:
            for _id in self.dungeon_instances.values():
                await ctx.bot.get_channel(_id['ROOM_ID']).delete()

            self.dungeon_instances = {}
            await ctx.send(f"```All dungeons reset.```")


def setup(bot):
    bot.add_cog(Server(bot))