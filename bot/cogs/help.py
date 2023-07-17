import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get some help :)")
    async def help(self, interaction: discord.Interaction):
      if interaction.user.guild_permissions.administrator:
        dm = await interaction.user.create_dm()
        owner_id = 'bbKubek'
        name = interaction.user
        embed = discord.Embed(title="Administrator Help Menu", colour=name.colour)
        embed.add_field(name="Bot owner", value=owner_id, inline=True)
        embed.add_field(name="Admin commands: ",
                        value="say, clear, secretdm, \n add, createticketmenu, delete, new, remove, startgive",
                        inline=False)
        embed.add_field(name="Prefix:", value="/", inline=True)
        embed.add_field(name="Latency:", value=f"{round(self.bot.latency * 1000)} ms", inline=True)
        await dm.send(embed=embed)

        owner_id = 'bbKubek'
        name = interaction.user
        embed = discord.Embed(title="Help Menu", colour=name.colour)
        embed.add_field(name="Bot owner", value=owner_id, inline=True)
        embed.add_field(name="Commands: ",
                        value="userinfo, botinfo, join, leave",
                        inline=False)
        embed.add_field(name="Prefix:", value="/", inline=True)
        embed.add_field(name="Latency:", value=f"{round(self.bot.latency * 1000)} ms", inline=True)
    
        embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot), guilds=[discord.Object(id=488258025665200129)])