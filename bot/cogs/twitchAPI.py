import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv
import requests
import os

class TwitchAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()
        self.client_id = os.getenv('TWITCH_CLIENT_ID')
        self.client_pass = os.getenv('TWITCH_CLIENT_PASS')

        self.streamer_name = 'muffler0'
        self.body = {
            'client_id': self.client_id,
            'client_secret': self.client_pass,
            "grant_type": 'client_credentials'
        }

        self.r = requests.post('https://id.twitch.tv/oauth2/token', self.body)
        self.keys = self.r.json()

        self.headers = {
            'Client-ID': self.client_id,
            'Authorization': 'Bearer ' + self.keys['access_token']
        }

    global is_muffler_live
    is_muffler_live = False
    @tasks.loop(minutes=1)
    async def check_twitch_stream(self):
        # Check Muffler
        global is_muffler_live
        stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + self.streamer_name, headers=self.headers)
        stream_data = stream.json()
        
        if len(stream_data['data']) == 1:
            if is_muffler_live == False:
                channel = self.bot.get_channel(826758257812832316)
                # print(stream_data['data'][0])
                embed = discord.Embed(title=stream_data['data'][0]['title'], url="https://www.twitch.tv/" + stream_data['data'][0]['user_login'], colour=discord.Color.purple())
                embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/408744552875163648/46eb06b02b67d8f42a22a5d4ae392c9f.webp?size=128")
                embed.set_author(name=stream_data['data'][0]['user_name'], icon_url="https://cdn.discordapp.com/avatars/408744552875163648/46eb06b02b67d8f42a22a5d4ae392c9f.webp?size=128")
                embed.set_image(url=stream_data['data'][0]['thumbnail_url'].replace('{width}', '350').replace('{height}', '200'))

                self.bot.statusloop.stop()
                await self.bot.change_presence(activity=discord.Streaming(name="Muffin is live!", url="https://www.twitch.tv/muffler0"))

                is_muffler_live = True
                await channel.send("<@&1119036686744178898> Muffin is live, come say hi :happymuffin:", embed=embed)
        else:
            try:
                self.bot.statusloop.start()
            except:
                pass

            is_muffler_live = False

async def setup(bot):
    await bot.add_cog(TwitchAPI(bot), guilds=[discord.Object(id=488258025665200129), discord.Object(id=743154237445242970)])