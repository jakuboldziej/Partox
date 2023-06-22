import discord
from discord.ext import commands, tasks
from discord import app_commands

import pytimeparse as parser
from datetime import datetime
from random import choice

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.gId = 1
        self.giveaways = list()
        self.color = discord.Color.blue()

        self.tasks = []

    @app_commands.command(name="startgive", description="starts a giveaway")
    @app_commands.describe(
        duration="duration of the giveaway", 
        winners="number of winners",
        prize="the prize being given away",
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
                
                    entries = list()
                    gId = self.gId
                    embed = None
                    btn = GiveawayButton(self, gId)

                    data = {
                        'id': gId,
                        'interaction': interaction,
                        'duration': duration,
                        'winners': winners,
                        'prize': prize,
                        'entries': entries,
                        'embed': embed,
                        'created_at': created_at,
                        'ended': False,
                        'btn': btn
                    }

                    self.giveaways.append(data)
                    
                    giveaway = next(giveaway for giveaway in self.giveaways if giveaway['id'] == gId)

                    embed = await self.create_embed(giveaway)
                    self.giveaways[gId - 1]['embed'] = embed

                    self.gId += 1

                    await interaction.response.send_message(embed=embed, view=btn)
                    self.task_launcher(data, 1)
            except:
                await interaction.response.send_message("Invalid time format! (1 minutes/1m)", ephemeral=True)
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)
          
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

    def task_launcher(self, data, interval):
        new_task = tasks.loop(seconds=interval)(self.manage_time)
        new_task.start(data)
        self.tasks.append([data['id'], new_task])

    async def manage_entries(self, data, user):
        if user not in data['entries']:
            data['entries'].append(user)
            embed_dict = data['embed'].to_dict()
            embed_dict['fields'][2]['value'] = f"Entries: {str(len(data['entries']))}"
            message = await data['interaction'].original_response()
            await message.edit(embed=discord.Embed.from_dict(embed_dict))

    async def manage_winners(self, data):
        entriesTemp = data['entries']
        winners = list()
        if len(entriesTemp) > 0:
            for _ in range(data['winners']):
                if len(entriesTemp) != 0:
                    randomWinner = choice(entriesTemp)
                    winners.append(randomWinner)
                    entriesTemp.remove(randomWinner)

            winnersText = ', '.join([winner.mention for winner in winners])

            embed_dict = data['embed'].to_dict()
            embed_dict['fields'][3]['value'] = f"Winners({data['winners']}): {winnersText}"
            message = await data['interaction'].original_response()
            await message.edit(embed=discord.Embed.from_dict(embed_dict))
        else:
            winnersText = ""
            embed_dict = data['embed'].to_dict()
            embed_dict['fields'][3]['value'] = f"Winners({data['winners']}): {winnersText}"
            message = await data['interaction'].original_response()
            await message.edit(embed=discord.Embed.from_dict(embed_dict))

        return winnersText 

    async def create_embed(self, data):
        embed = discord.Embed(title=data['prize'], color=self.color)
        embed.add_field(name="", value=f"Ends: <t:{str(data['duration'])}:R> (<t:{round(data['created_at'].timestamp())}:f>)")
        embed.add_field(name="", value=f"Hosted by: {data['interaction'].user.mention}", inline=False)
        embed.add_field(name="", value=f"Entries: {str(len(data['entries']))}", inline=False)
        embed.add_field(name="", value=f"Winners: {str(data['winners'])}", inline=False)
        embed.set_footer(text=f"ID: {data['id']}")
        return embed

class GiveawayButton(discord.ui.View):
    def __init__(self, giveaway: Giveaway, gId):
        super().__init__()
        self.value = None
        self.gId = gId
        self.giveaway = giveaway

    @discord.ui.button(label="🎉", style=discord.ButtonStyle.primary)
    async def enterGiveawayBtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        for gEl in self.giveaway.giveaways:
            if gEl['id'] == self.gId:
                if interaction.user not in gEl['entries']:
                    await interaction.response.send_message(f"{interaction.user.mention}! You entered the giveaway!", ephemeral=True)
                    await self.giveaway.manage_entries(gEl, interaction.user)
                else:
                    await interaction.response.send_message(f"{interaction.user.mention}! You already entered the giveaway!", ephemeral=True, delete_after=10)

async def setup(bot):
    await bot.add_cog(Giveaway(bot), guilds=[discord.Object(id=488258025665200129)])
    # await bot.add_cog(Giveaway(bot))