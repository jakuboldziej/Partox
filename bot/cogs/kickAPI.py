import discord
from discord.ext import commands, tasks

import requests

class KickAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=1)
    async def check_kick_stream(self):
        stream = requests.get('https://kick.com/api/v2/channels/muffler0')
        # stream_data = stream.json()
        
        # if len(stream_data['data']) == 1:
        #     if is_muffler_live == False:
        #         channel = self.bot.get_channel(1119064100778029139)
        #         # print(stream_data['data'][0])
        #         embed = discord.Embed(title=stream_data['data'][0]['title'], url="https://www.twitch.tv/" + stream_data['data'][0]['user_login'], colour=discord.Color.green())
        #         embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/408744552875163648/46eb06b02b67d8f42a22a5d4ae392c9f.webp?size=128")
        #         embed.set_author(name=stream_data['data'][0]['user_name'], icon_url="https://cdn.discordapp.com/avatars/408744552875163648/46eb06b02b67d8f42a22a5d4ae392c9f.webp?size=128")
        #         embed.set_image(url=stream_data['data'][0]['thumbnail_url'].replace('{width}', '350').replace('{height}', '200'))

        #         is_muffler_live = True
        #         await channel.send("<@&1119036686744178898> Muffin is live, come say hi :happymuffin:", embed=embed)
        # else:
        #     is_muffler_live = False

async def setup(bot):
    await bot.add_cog(KickAPI(bot))