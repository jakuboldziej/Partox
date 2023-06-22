import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get

from asyncio import sleep
from datetime import datetime, timedelta

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = list()
        self.tId = 1
    
    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'Synced {len(fmt)} commands.')

    @app_commands.command(name="createticketmenu", description="Create ticket menu")
    async def createTicketMenu(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
          embed = discord.Embed(title="Create your tickets here", color=discord.Color.dark_green())
          embed.add_field(name="", value="To create a ticket react with 📩")

          await interaction.response.send_message(embed=embed, view=TicketButton(self, "create_new_ticket"))
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)

    @app_commands.command(name="new", description="Create a ticket")
    @app_commands.describe(
        user="User to create ticket with", 
        reason="The reason for creating this ticket", 
    )
    async def newTicket(self, interaction: discord.Interaction, user: discord.Member = None, reason: str = None):
        if interaction.user.guild_permissions.administrator:
          await self.create_new_ticket(interaction, reason)
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)

    async def create_new_ticket(self, interaction, reason = None):
        guild = interaction.guild
        tId = self.tId
        
        support_role = get(guild.roles, id=488328320497221632)

        overwrites = {
          guild.default_role: discord.PermissionOverwrite(view_channel=False),
          interaction.user: discord.PermissionOverwrite(view_channel=True),
          support_role: discord.PermissionOverwrite(view_channel=True),
        }
        
        if interaction.user is not None:
          overwrites[interaction.user] = discord.PermissionOverwrite(view_channel=True)
          
        channel = await guild.create_text_channel(f'ticket-{tId}', overwrites=overwrites)
        
        if reason is not None:
            embed = discord.Embed(title=f"Ticket ID: {tId}", color=discord.Color.green())
            embed.add_field(name="Reason of the ticket: ", value=reason, inline=False)
            embed.add_field(name="Creator of the ticket: ", value=interaction.user.mention, inline=False)
            await channel.send(f'Welcome {interaction.user.mention}', embed=embed, view=TicketButton(self, "close_ticket", tId))
        else:
            embed = discord.Embed(title=f"Ticket ID: {tId}", color=discord.Color.green())
            embed.add_field(name="Creator of the ticket: ", value=interaction.user.mention, inline=False)
            await channel.send(f'Welcome {interaction.user.mention}', embed=embed, view=TicketButton(self, "close_ticket", tId))
           
        self.tickets.append({'tId': tId, 'users': [interaction.user,], 'closed': False})
        self.tId += 1

        return channel

    @app_commands.command(name="add", description="Add user to the ticket")
    @app_commands.describe(
        user="Add user to this ticket", 
    )
    async def add_user_to_ticket(self, interaction: discord.Interaction, user: discord.Member):
        if interaction.user.guild_permissions.administrator:
          # await interaction.channel.set_permissions(user, read_messages=True)
          # await interaction.channel.set_permissions(user, read_message_history=True)
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
          # await interaction.channel.set_permissions(user, read_messages=True)
          # await interaction.channel.set_permissions(user, read_message_history=True)
          await interaction.channel.set_permissions(user, view_channel=False)
          
          channel = interaction.channel.mention
          await interaction.response.send_message(f'{user.mention} removed from the ticket {channel}')
        else:
          await interaction.response.send_message("You don't have permissions to use this.", ephemeral=True)

    @app_commands.command(name="delete", description="Delete the current ticket")
    @app_commands.describe(
        reason="The reason for deleting this ticket", 
    )
    async def deleteTicket(self, interaction: discord.Interaction, reason: str = None):
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

class TicketButton(discord.ui.View):
    def __init__(self, ticket: Ticket, event, tId = None):
        super().__init__()
        self.value = None
        self.ticket = ticket
        self.event = event
        self.tId = tId
        self.buttons = list()
        self.add_buttons()

    def add_buttons(self):
      if self.event == "create_new_ticket":
        async def createNewTicketBtn(interaction: discord.Interaction):
          channel = await self.ticket.create_new_ticket(interaction)
          await interaction.response.send_message(f"Ticket created {channel.mention}", ephemeral=True)

        createNewTicket = [discord.ui.Button(label="📩 Create ticket", style=discord.ButtonStyle.secondary), createNewTicketBtn]

        self.buttons.append(createNewTicket)

      elif self.event == "close_ticket":
        async def closeTicketBtn(interaction: discord.Interaction):
          current_ticket = next(item for item in self.ticket.tickets if item["tId"] == self.tId)

          if not current_ticket['closed']:
            embed1 = discord.Embed(title="", color=discord.Color.red())
            embed1.add_field(name="", value=f"Ticket closed by: {interaction.user.mention}")
            embed2 = discord.Embed(title="Support team ticket controls", color=discord.Color.darker_grey())

            current_ticket['closed'] = True

            await interaction.response.defer()
            await interaction.channel.send(embed=embed1)
            await interaction.channel.send(embed=embed2, view=TicketButton(self.ticket, "support_controls", current_ticket['tId']))
            await interaction.channel.edit(name=f"closed-{self.tId}")
            # await interaction.channel.set_permissions(current_ticket['user'], read_messages=False)
            # await interaction.channel.set_permissions(current_ticket['user'], read_message_history=False)
            await next(interaction.channel.set_permissions(user, view_channel=False) for user in current_ticket['users'])
          else:
            await interaction.response.send_message("Warning: ticket already closed", ephemeral=True)

        close_ticket = [discord.ui.Button(label="🔒 Close ", style=discord.ButtonStyle.secondary), closeTicketBtn]

        self.buttons.append(close_ticket)
      
      elif self.event == "support_controls":
        async def openTicketBtn(interaction: discord.Interaction):
          current_ticket = next(item for item in self.ticket.tickets if item["tId"] == self.tId)

          embed = discord.Embed(title="", color=discord.Color.green())
          embed.add_field(name="", value=f"Ticket Opened by: {interaction.user.mention}")
          
          current_ticket['closed'] = False

          await interaction.response.defer()
          await interaction.channel.send(embed=embed)
          await interaction.delete_original_response()
          await interaction.channel.edit(name=f"ticket-{self.tId}")
             
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
    await bot.add_cog(Ticket(bot), guilds=[discord.Object(id=488258025665200129)])