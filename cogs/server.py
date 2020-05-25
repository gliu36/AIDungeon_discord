import discord
from discord.ext import commands

class Server(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dungeon_master = None
        self.dungeon_master_id = None

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('ni hao1')

    @commands.command()
    async def test(self, ctx, x):
        await ctx.send(x)

    @commands.command()
    async def become_dm(self, ctx):
        if not self.dungeon_master_id:
            self.dungeon_master = ctx.author
            self.dungeon_master_id = ctx.author.id
            await ctx.send(f"```{self.dungeon_master} is now the dungeon master.```")
        else:
            await ctx.send(f"```{self.dungeon_master} is already the dungeon master. Use '>>restart' to restart dungeon.```")


    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"```Cleared {amount} messages```")

    @commands.command()
    async def restart(self, ctx):
        self.dungeon_master = None
        self.dungeon_master_id = None
        await self.clear(ctx, amount=100)
        await ctx.send(f"```Dungeon reset.```")


def setup(bot):
    bot.add_cog(Server(bot))