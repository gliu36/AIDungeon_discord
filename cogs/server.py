import discord
from discord.ext import commands

GUILD_ID = 714294408572567574

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
    async def say(self, ctx, x):
        await ctx.send(x)

    @commands.command()
    async def new_game(self, ctx):
        name = ctx.author.name
        _id = ctx.author.id

        if ctx.author.id in self.dungeon_instances.keys():
            await ctx.send(f"{ctx.author.mention} You already have a dungeon: {ctx.bot.get_channel(self.dungeon_instances[_id]).mention}. Use '>>restart' to restart your dungeon.")
        else:
            guild = ctx.bot.get_guild(GUILD_ID)
            channel = await guild.create_text_channel(f"{name}_dungeon")

            await ctx.send(f"{ctx.author.mention} is now the dungeon master of {channel.mention}.")

            # Only 1 instance per user
            self.dungeon_instances[ctx.author.id] = channel.id


    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"```Cleared {amount} messages```")

    @commands.command()
    async def restart(self, ctx):
        a = ctx.author
        await ctx.bot.get_channel(self.dungeon_instances[a.id]).delete()
        del self.dungeon_instances[a.id]
        await ctx.send(f"{ctx.author.mention} Your dungeon is cleared.")

    @commands.command()
    async def restart_all(self, ctx):
        for _id in self.dungeon_instances.values():
            await ctx.bot.get_channel(_id).delete()

        self.dungeon_instances = {}
        # await self.clear(ctx, amount=100)
        await ctx.send(f"```All dungeons reset.```")


def setup(bot):
    bot.add_cog(Server(bot))