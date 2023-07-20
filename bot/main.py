import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions

from dotenv import load_dotenv, find_dotenv
from itertools import cycle
import os

from cogs.twitchAPI import TwitchAPI

load_dotenv(find_dotenv())

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activity_list = cycle(["/help", "Author: bbKubek"])

    async def load_extensions(self):
        path = os.listdir(os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'cogs')))
        for filename in path:
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        print(f"{len([filename for filename in path if filename.endswith('.py')])} cogs loaded.")

    @tasks.loop(seconds=30)
    async def statusloop(self):
        await bot.change_presence(activity=discord.Game(next(self.activity_list)))

    async def on_ready(self):
        await self.wait_until_ready()
        await self.load_extensions()

        self.statusloop.start()
        TwitchAPI(self).check_twitch_stream.start()
        print(f"{self.user} is online.")

    async def on_command_error(self, ctx, error):
        author = ctx.message.author.mention
        dm = await ctx.author.create_dm()

        if isinstance(error, commands.CommandNotFound):
            try:
                await ctx.send(f"{author} no command found", delete_after=10)
                await dm.send("Check the command list at /help")
            except:
                raise error

        if isinstance(error, MissingPermissions):
            await ctx.send("Sorry, you do not have permissions to do that!", delete_after=5)

bot = Bot(command_prefix="/", intents=intents)
bot.remove_command("help")

#%% Commands

@has_permissions(administrator=True)
@bot.command(name="clear")
@commands.cooldown(1, 10.0, commands.BucketType.user)
async def clear_messages(ctx, limit=15):
  if 0 < limit <= 15:
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit)
    await ctx.send(f"Deleted {limit} messages.", delete_after=5)
  else:
    await ctx.send("Limit: 15", delete_after=5)

@has_permissions(administrator=True)
@bot.command(pass_context=True)
async def secretdm(ctx, userId, message=None):
    await ctx.message.delete()
    user = await bot.fetch_user(userId)
    await user.send(message)

@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(title="Bot Info", colour=0xff7e00)
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/rZt1H5zBMFY6SgDYqKpG_e7km31WyEtC3-esRGcPUCc/%3Fsize%3D1024/https/cdn.discordapp.com/icons/488258025665200129/eb73ae8f29850e35685834409195809c.webp")
    embed.add_field(name="Bot name", value=bot.user.name)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Library", value="discord.py", inline=False)
    embed.add_field(name="Created by", value="bbKubek", inline=False)

    embed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx):
    name = ctx.message.author
    display_name = name.display_name

    embed = discord.Embed(title="User Info", colour=name.colour)
    embed.set_author(name=display_name)
    embed.add_field(name="Created at",
                    value=name.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                    inline=True)
    embed.add_field(name="Joined at",
                    value=name.joined_at.strftime("%d/%m/%Y %H:%M:%S"),
                    inline=True)
    embed.add_field(name="User ID", value=name.id, inline=False)
    embed.add_field(name="Top Role", value=name.top_role.mention, inline=True)

    embed.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=embed)

@has_permissions(administrator=True)
@bot.command()
async def say(ctx, message=None):
    await ctx.message.delete()
    await ctx.send(message)

@has_permissions(administrator=True)
@bot.command()
@commands.cooldown(1, 10.0, commands.BucketType.user)
async def clear_messages(ctx, limit=15):
  if 0 < limit <= 15:
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit)
    await ctx.send(f"Deleted {limit} messages.", delete_after=5)
  else:
    await ctx.send("Limit usuwanych wiadomości \n Limit: 15", delete_after=5)

@bot.command(pass_context=True)
async def join(ctx):
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Dołącz na kanał głosowy.", delete_after=15)

@bot.command(pass_context=True)
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))