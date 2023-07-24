import discord
from discord.ext import commands, tasks
from discord import app_commands

import aiohttp
import pytimeparse as parser
from datetime import datetime
from random import choice
import os

class Giveaway(commands.Cog):
    def __init__(self, bot):
        # self.url = os.getenv("API_URL_LOCALHOST")
        self.url = os.getenv("API_URL_PARTOX")
        self.bot = bot

        self.id = 1
        self.giveaways = list()
        self.color = discord.Color.blue()

        self.tasks = []
        self.bot.loop.create_task(self.get_giveaways())

    @app_commands.command(name="startgive", description="starts a giveaway")
    @app_commands.describe(
        duration="duration of the giveaway", 
        winners="number of winners",
        prize="the prize being given away + title of this giveaway",
    )
    async def startgive(self, interaction: discord.Interaction, duration: str, winners: int, prize: str):
        if interaction.user.guild_permissions.administrator:
            try:
                if (winners <= 0):
                    await interaction.response.send_message("Type non-negative number of winners!", ephemeral=True)
                else:
                    created_at = datetime.now()
                    duration = parser.parse(duration)
                    duration = duration + round(created_at.timestamp())
                
                    try:        
                        last_id = self.giveaways.pop()['id']
                        self.id = int(last_id) + 1
                    except:
                        self.id = 1

                    self.bot.loop.create_task(self.create_giveaway({
                        'guild_id': interaction.guild.id,
                        'prize': prize,
                        'entries': None,
                        'winners': None,
                        'possible_winners': winners,
                        'duration': str(datetime.fromtimestamp(duration)),
                        'created_at': str(created_at),
                        'ended': False,
                    }))

                    data = {
                        'id': self.id,
                        'guild_id': interaction.guild.id,
                        'interaction': interaction,
                        'prize': prize,
                        'entries': [],
                        'winners': [],
                        'possible_winners': winners,
                        'duration': duration,
                        'created_at': created_at,
                        'ended': False,
                    }

                    embed = await self.create_embed(data)
                    data['embed'] = embed

                    btn = GiveawayButton(self, self.id, data)
                    data['btn'] = btn

                    await interaction.response.send_message(embed=embed, view=btn)
                    self.task_launcher(data, 1)

            except:
                await interaction.response.send_message("Invalid time format! (1 minutes/1m)", ephemeral=True)
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)
          
    # Functionality

    async def manage_time(self, data):
        duration = datetime.fromtimestamp(data['duration'])
        currentTime = datetime.now()
        if (currentTime >= duration):
            if len(data['entries']) > 0:
                winnersText = await self.manage_winners(data)
                await data['interaction'].followup.send(f"Congratulations {winnersText}! You won the {data['prize']}!")
            else:
                await data['interaction'].followup.send("No valid entrants, so a winner could not be determined!")

            embed_dict = data['embed'].to_dict()
            embed_dict['fields'][0]['value'] = f"Ended: <t:{str(data['duration'])}:R> (<t:{round(data['created_at'].timestamp())}:f>)"
            message = await data['interaction'].original_response()
            await message.edit(embed=discord.Embed.from_dict(embed_dict), view=None)

            for giveaway in self.giveaways:
                if giveaway['id'] == data['id']:
                    giveaway['ended'] = True

            for task in self.tasks:
                if task[0] == data['id']:
                    task[1].stop()

            await self.end_giveaway(data)
            
    def task_launcher(self, data, interval):
        new_task = tasks.loop(seconds=interval)(self.manage_time)
        new_task.start(data)
        self.tasks.append([data['id'], new_task])

    async def manage_entries(self, data, user):
        if user.name not in data['entries']:
            data['entries'].append(user)

            embed_dict = data['embed'].to_dict()
            embed_dict['fields'][2]['value'] = f"Entries: {str(len(data['entries']))}"
            message = await data['interaction'].original_response()
            await message.edit(embed=discord.Embed.from_dict(embed_dict))

            data_json = await self.convert_to_str(data)
            data_to_send = {
                'guild_id': data_json['guild_id'],
                'prize': data_json['prize'],
                'entries': data_json['entries'],
                'winners': data_json['winners'],
                'possible_winners': data_json['possible_winners'],
                'duration': str(datetime.fromtimestamp(data_json['duration'])),
                'created_at': str(data_json['created_at']),
                'ended': data_json['ended'],
            }
            endpoint = self.url + f"/add-giveaway-entry/{str(data['id'])}"
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=data_to_send) as r:
                    if r.status == 200:
                        await self.get_giveaways()

    async def manage_winners(self, data):
        giveaway_entries = data['entries']
        guild = self.bot.get_guild(data['guild_id'])
        guild_members = guild.members
        data['entries'] = []
        for user in guild_members:
            if user.name in giveaway_entries:
                data['entries'].append(user)
    
        entriesTemp = data['entries']
        winners = list()
        if len(entriesTemp) > 0:
            for _ in range(data['possible_winners']):
                if len(entriesTemp) != 0:
                    randomWinner = choice(entriesTemp)
                    winners.append(randomWinner)
                    entriesTemp.remove(randomWinner)
            data['winners'] = winners
            winnersText = ', '.join([winner.mention for winner in winners])

            embed_dict = data['embed'].to_dict()
            embed_dict['fields'][3]['value'] = f"Winners({data['possible_winners']}): {winnersText}"
            message = await data['interaction'].original_response()
            await message.edit(embed=discord.Embed.from_dict(embed_dict))
        else:
            winnersText = ""
            embed_dict = data['embed'].to_dict()
            embed_dict['fields'][3]['value'] = f"Winners({data['possible_winners']}): {winnersText}"
            message = await data['interaction'].original_response()
            await message.edit(embed=discord.Embed.from_dict(embed_dict))
        
        return winnersText

    async def create_embed(self, data):
        embed = discord.Embed(title=data['prize'], color=self.color)
        embed.add_field(name="", value=f"Ends: <t:{str(data['duration'])}:R> (<t:{str(round(data['created_at'].timestamp()))}:f>)")
        embed.add_field(name="", value=f"Hosted by: {data['interaction'].user.mention}", inline=False)
        embed.add_field(name="", value=f"Entries: {str(len(data['entries']))}", inline=False)
        embed.add_field(name="", value=f"Winners: {str(data['possible_winners'])}", inline=False)
        embed.set_footer(text=f"Giveaway ID: {data['id']}")
        return embed

    async def convert_to_member(self, giveaways):
        try:
            for giveaway in giveaways:
                giveaway_entries = giveaway['entries']
                guild = self.bot.get_guild(giveaway['guild_id'])
                guild_members = guild.members

                giveaway['entries'] = []
                for user in guild_members:
                    if user.name in giveaway_entries:
                        giveaway['entries'].append(user)
                return giveaways
        except:
            return giveaways

    async def convert_to_str(self, giveaway):
        giveaway_entries = list(giveaway['entries'])
        giveaway_winners = list(giveaway['winners'])
        guild = self.bot.get_guild(giveaway['guild_id'])
        guild_members = guild.members

        for member in giveaway_entries:
            if not isinstance(member, str) and member in guild_members:
                giveaway['entries'].remove(member)
                giveaway['entries'].append(member.name)

        for member in giveaway_winners:
            if not isinstance(member, str) and member in guild_members:
                giveaway['winners'].remove(member)
                giveaway['winners'].append(member.name)

        return giveaway

    # API Requests
    async def get_giveaways(self):
      endpoint = self.url + "/get-giveaways/"
      async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as r:
            if r.status == 200:
                giveaways = await self.convert_to_member(await r.json())
                self.giveaways = giveaways
                print("fetched giveaways")

    async def create_giveaway(self, data):
        endpoint = self.url + "/create-giveaway/"
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=data) as r:
                if r.status == 200:
                    await self.get_giveaways()

    async def end_giveaway(self, data):
        data['ended'] = True
        data_json = await self.convert_to_str(data)
        
        data_to_send = {
            'guild_id': data_json['guild_id'],
            'prize': data_json['prize'],
            'winners': data_json['winners'],
            'possible_winners': data_json['possible_winners'],
            'duration': str(datetime.fromtimestamp(data_json['duration'])),
            'created_at': str(data_json['created_at']),
            'ended': data_json['ended'],
        }

        endpoint = self.url + f"/end-giveaway/{str(data['id'])}"
        async with aiohttp.ClientSession() as session:
          async with session.post(endpoint, json=data_to_send) as r:
              if r.status == 200:
                await self.get_giveaways()

class GiveawayButton(discord.ui.View):
    def __init__(self, giveaway: Giveaway, gId, data):
        super().__init__()
        self.value = None
        self.gId = gId
        self.giveaway = giveaway
        self.data = data

    @discord.ui.button(label="🎉", style=discord.ButtonStyle.primary)
    async def enterGiveawayBtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.name not in self.data['entries']:
            await interaction.response.send_message(f"{interaction.user.mention}! You entered the giveaway!", ephemeral=True)
            await self.giveaway.manage_entries(self.data, interaction.user)
        else:
            await interaction.response.send_message(f"{interaction.user.mention}! You already entered the giveaway!", ephemeral=True, delete_after=10)

async def setup(bot):
    await bot.add_cog(Giveaway(bot), guilds=[discord.Object(id=488258025665200129), discord.Object(id=743154237445242970)])
    # await bot.add_cog(Giveaway(bot))