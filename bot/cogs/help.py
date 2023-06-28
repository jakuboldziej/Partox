import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def help(self, ctx, command=None):
      if ctx.message.author.guild_permissions.administrator:
          dm = await ctx.author.create_dm()
          owner_id = 'bbKubek'
          name = ctx.message.author
          embed = discord.Embed(title="Administrator Help Menu", colour=name.colour)
          embed.add_field(name="Bot owner", value=owner_id, inline=True)
          embed.add_field(name="Admin commands: ",
                          value="say, clear, secretdm, \n add, createticketmenu, delete, new, remove, startgive",
                          inline=False)
          embed.add_field(name="Prefix:", value="/p", inline=True)
          embed.add_field(name="Latency:", value=f"{round(self.bot.latency * 1000)} ms", inline=True)
          await dm.send(embed=embed)

      owner_id = 'bbKubek'
      name = ctx.message.author
      embed = discord.Embed(title="Help Menu", colour=name.colour)
      embed.add_field(name="Bot owner", value=owner_id, inline=True)
      embed.add_field(name="Commands: ",
                      value="userinfo, botinfo, join, leave",
                      inline=False)
      embed.add_field(name="Prefix:", value="/p", inline=True)
      embed.add_field(name="Latency:", value=f"{round(self.bot.latency * 1000)} ms", inline=True)

      embed.set_footer(text=f"Requested by {ctx.author}")
      await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))