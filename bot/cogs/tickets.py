import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get

import aiohttp
from asyncio import sleep
from datetime import datetime, timedelta
import os

class Ticket(commands.Cog):
    def __init__(self, bot):
        # self.url = os.getenv("API_URL_LOCALHOST")
        self.url = os.getenv("API_URL_PARTOX")
        self.bot = bot
        
        self.tickets = list()
        self.id = 1

        self.bot.loop.create_task(self.get_tickets())

    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'Synced {len(fmt)} commands.')

    # Commands
    @app_commands.command(name="createticketmenu", description="Create ticket menu")
    @app_commands.describe(
        title="Title of the panel", 
    )
    async def createTicketMenu(self, interaction: discord.Interaction, title: str = "Create your tickets here"):
        if interaction.user.guild_permissions.administrator:
          embed = discord.Embed(title=title, color=discord.Color.dark_green())
          embed.add_field(name="", value="To create a ticket react with 📩")

          await interaction.response.send_message(embed=embed, view=TicketButton(self, "create_new_ticket", timeout=None))
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)

    @app_commands.command(name="new", description="Create a ticket")
    @app_commands.describe(
        user="User to create ticket with", 
        reason="The reason for creating this ticket", 
    )
    async def new_ticket(self, interaction: discord.Interaction, user: discord.Member = None, reason: str = None):
        if interaction.user.guild_permissions.administrator:
          channel = await self.create_new_ticket(interaction)
          await interaction.response.send_message(f"Ticket created {channel.mention}", ephemeral=True)
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)

    @app_commands.command(name="add", description="Add user to the ticket")
    @app_commands.describe(
        user="Add user to this ticket", 
    )
    async def add_user_to_ticket(self, interaction: discord.Interaction, user: discord.Member):
        if interaction.user.guild_permissions.administrator:
          self.bot.loop.create_task(self.update_ticket_users(interaction.channel.name.split("-")[1], user, "add"))
          await interaction.channel.set_permissions(user, view_channel=True)
          
          channel = interaction.channel.mention
          await interaction.response.send_message(f'{user.mention} added to ticket {channel}')
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)

    @app_commands.command(name="remove", description="Remove user from the ticket")
    @app_commands.describe(
        user="Remove user from this ticket", 
    )
    async def remove_user_from_ticket(self, interaction: discord.Interaction, user: discord.Member):
        if interaction.user.guild_permissions.administrator:
          self.bot.loop.create_task(self.update_ticket_users(interaction.channel.name.split("-")[1], user, "remove"))
          await interaction.channel.set_permissions(user, view_channel=False)
          
          channel = interaction.channel.mention
          await interaction.response.send_message(f'{user.mention} removed from the ticket {channel}')
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)

    @app_commands.command(name="delete", description="Delete the current ticket")
    @app_commands.describe(
        reason="The reason for deleting this ticket", 
    )
    async def delete_ticket(self, interaction: discord.Interaction, reason: str = None):
        if interaction.user.guild_permissions.administrator:
          currentChannel = interaction.channel
          channel_split = currentChannel.name.split("-")

          if channel_split[0] == "ticket" or channel_split[0] == "closed":
              duration = datetime.now() + timedelta(seconds=5)

              await interaction.response.send_message(f"Ticket will be deleted <t:{round(duration.timestamp())}:R>.")
              await sleep(5)
              await currentChannel.delete()
          else:
              await interaction.response.send_message("This channel isn't a ticket", ephemeral=True)
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)

    # Functionality
    async def create_new_ticket(self, interaction, reason = None):
        guild = interaction.guild

        try:        
          last_id = self.tickets.pop()['id']
          self.id = int(last_id) + 1
        except:
           self.id = 1

        overwrites = {
          guild.default_role: discord.PermissionOverwrite(view_channel=False),
          interaction.user: discord.PermissionOverwrite(view_channel=True),
        }
        
        if interaction.user is not None:
          overwrites[interaction.user] = discord.PermissionOverwrite(view_channel=True)

        print(guild.id, overwrites)  
        
        channel = await guild.create_text_channel(f'ticket-{self.id}', overwrites=overwrites)
        
        if reason is not None:
            embed = discord.Embed(title=f"Ticket ID: {self.id}", color=discord.Color.green())
            embed.add_field(name="Reason of the ticket: ", value=reason, inline=False)
            embed.add_field(name="Creator of the ticket: ", value=interaction.user.mention, inline=False)
            await channel.send(f'Welcome {interaction.user.mention}', embed=embed, view=TicketButton(self, "close_ticket", self.id))
        else:
            embed = discord.Embed(title=f"Ticket ID: {self.id}", color=discord.Color.green())
            embed.add_field(name="Creator of the ticket: ", value=interaction.user.mention, inline=False)
            await channel.send(f'Welcome {interaction.user.mention}', embed=embed, view=TicketButton(self, "close_ticket", self.id))

        data = {
           'guild_id': guild.id,
           'users': [interaction.user.name],
           'closed': False,
           'created_at': str(datetime.now())
        }
        self.bot.loop.create_task(self.create_ticket(data))

        return channel
    
    async def convert_to_member(self, tickets):
        for ticket in tickets:
          ticket_users = ticket['users']
          guild = self.bot.get_guild(ticket['guild_id'])
          guild_members = guild.members

          ticket['users'] = []
          for user in guild_members:
            if user.name in ticket_users:
                ticket['users'].append(user)

        return tickets

    async def convert_to_str(self, ticket):
        ticket_users = ticket['users']
        guild = self.bot.get_guild(ticket['guild_id'])
        guild_members = guild.members

        ticket['users'] = [member.name for member in ticket_users if member in guild_members]
        return ticket

    # API Requests
    async def get_tickets(self):
      endpoint = self.url + "/get-tickets/"
      async with aiohttp.ClientSession() as session:
         async with session.get(endpoint) as r:
            if r.status == 200:
              tickets = await self.convert_to_member(await r.json())
              self.tickets = tickets
              print("fetched tickets")

    async def get_ticket(self, ticket_id):
      endpoint = self.url + f"/get-ticket/{ticket_id}"
      async with aiohttp.ClientSession() as session:
         async with session.get(endpoint) as r:
            if r.status == 200:
              print("fetched one")

    async def create_ticket(self, data):
        endpoint = self.url + "/create-ticket/"
        async with aiohttp.ClientSession() as session:
         async with session.post(endpoint, json=data) as r:
            if r.status == 200:
               await self.get_tickets()

    async def update_ticket_users(self, ticket_id, user, type):
      for ticket in self.tickets:
        if ticket['id'] == ticket_id:
          ticket = ticket

      if type == "add":
        if user not in ticket['users']:
          ticket['users'].append(user)

          ticket_json = await self.convert_to_str(ticket)      

          endpoint = self.url + f"/add-user-to-ticket/{ticket_id}"
          async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=ticket_json) as r:
                if r.status == 200:
                  await self.get_tickets()
      else:
        if user in ticket['users']:
          ticket['users'].remove(user)

          ticket_json = await self.convert_to_str(ticket)      

          endpoint = self.url + f"/remove-user-from-ticket/{ticket_id}"
          async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=ticket_json) as r:
                if r.status == 200:
                  await self.get_tickets()

    async def manage_close_ticket(self, ticket_id, type):
      for ticket in self.tickets:
        if ticket['id'] == ticket_id:
          ticket = ticket
          
      if type == "close":
        ticket['closed'] = True
        ticket_json = await self.convert_to_str(ticket) 

        endpoint = self.url + f"/close-ticket/{ticket_id}"
        async with aiohttp.ClientSession() as session:
          async with session.post(endpoint, json=ticket_json) as r:
              if r.status == 200:
                await self.get_tickets()
              else:
                 print(r.status)
      else:
        ticket['closed'] = False
        ticket_json = await self.convert_to_str(ticket) 
        endpoint = self.url + f"/open-ticket/{ticket_id}"
        async with aiohttp.ClientSession() as session:
          async with session.post(endpoint, json=ticket_json) as r:
              if r.status == 200:
                await self.get_tickets()
              else:
                 print(r.status)

class TicketButton(discord.ui.View):
    def __init__(self, ticket: Ticket, event, id = None):
        super().__init__(timeout=None)
        self.value = None
        self.ticket = ticket
        self.event = event
        self.id = id
        self.buttons = list()
        self.add_buttons()

        self.cooldown_time = 10
        self.cooldown = commands.CooldownMapping.from_cooldown(1, self.cooldown_time, commands.BucketType.member)

    def add_buttons(self):
      if self.event == "create_new_ticket":
        async def createNewTicketBtn(interaction: discord.Interaction):
          bucket = self.cooldown.get_bucket(interaction.message)
          retry = bucket.update_rate_limit()
          if retry:
            return await interaction.response.send_message(f"Slow down! Try again in {round(retry, 1)} seconds.", ephemeral=True)
          
          channel = await self.ticket.create_new_ticket(interaction)
          await interaction.response.send_message(f"Ticket created {channel.mention}", ephemeral=True)

        createNewTicket = [discord.ui.Button(label="📩 Create ticket", style=discord.ButtonStyle.secondary), createNewTicketBtn]

        self.buttons.append(createNewTicket)

      elif self.event == "close_ticket":
        async def closeTicketBtn(interaction: discord.Interaction):
          channel_id = str(interaction.channel).split("-")[1]

          current_ticket = next(ticket for ticket in self.ticket.tickets if int(ticket['id']) == int(channel_id))

          if not current_ticket['closed']:
            embed1 = discord.Embed(title="", color=discord.Color.red())
            embed1.add_field(name="", value=f"Ticket closed by: {interaction.user.mention}")
            embed2 = discord.Embed(title="Support team ticket controls", color=discord.Color.darker_grey())

            current_ticket['closed'] = True

            await interaction.response.defer()
            await interaction.channel.send(embed=embed1)
            await interaction.channel.send(embed=embed2, view=TicketButton(self.ticket, "support_controls", current_ticket['id']))
            await interaction.channel.edit(name=f"closed-{self.id}")
            await next(interaction.channel.set_permissions(user, view_channel=False) for user in current_ticket['users'])
            self.ticket.bot.loop.create_task(self.ticket.manage_close_ticket(interaction.channel.name.split("-")[1], "close"))
          else:
            await interaction.response.send_message("Warning: ticket already closed", ephemeral=True)

        close_ticket = [discord.ui.Button(label="🔒 Close ", style=discord.ButtonStyle.secondary), closeTicketBtn]

        self.buttons.append(close_ticket)
      
      elif self.event == "support_controls":
        async def openTicketBtn(interaction: discord.Interaction):
          current_ticket = next(item for item in self.ticket.tickets if item["id"] == self.id)

          embed = discord.Embed(title="", color=discord.Color.green())
          embed.add_field(name="", value=f"Ticket Opened by: {interaction.user.mention}")
          
          current_ticket['closed'] = False

          await interaction.response.defer()
          await interaction.channel.send(embed=embed)
          await interaction.delete_original_response()
          await interaction.channel.edit(name=f"ticket-{self.id}")
          self.ticket.bot.loop.create_task(self.ticket.manage_close_ticket(interaction.channel.name.split("-")[1], "open"))
             
        async def deleteTicketBtn(interaction: discord.Interaction):
          currentChannel = interaction.channel
          duration = datetime.now() + timedelta(seconds=5)

          await interaction.response.send_message(f"Ticket will be deleted <t:{round(duration.timestamp())}:R>.")
          await sleep(5)
          await currentChannel.delete()

        open_ticket = [discord.ui.Button(label="🔓 Open", style=discord.ButtonStyle.secondary), openTicketBtn]
        delete_ticket = [discord.ui.Button(label="⛔ Delete", style=discord.ButtonStyle.secondary), deleteTicketBtn]
        self.buttons.append(open_ticket)
        self.buttons.append(delete_ticket)
        
      for button in self.buttons:
         button[0].callback = button[1]
         self.add_item(button[0])
          
async def setup(bot):
    await bot.add_cog(Ticket(bot), guilds=[discord.Object(id=488258025665200129), discord.Object(id=743154237445242970)])