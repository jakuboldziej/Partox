import discord
from discord.ext import commands

class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Moyai listener
        if "moyai" in message.content:
          await message.add_reaction("🗿")

async def setup(bot):
    await bot.add_cog(Listener(bot))