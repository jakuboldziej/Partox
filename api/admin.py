from django.contrib import admin

from .models import Ticket, Giveaway

class TicketAdmin(admin.ModelAdmin):
    fields = ['users', 'closed', 'guild_id', 'created_at']
    list_display = ['id', 'users', 'closed', 'guild_id', 'created_at']

admin.site.register(Ticket, TicketAdmin)

class GiveawayAdmin(admin.ModelAdmin):
    fields = ['guild_id', 'prize', 'entries', 'winners', 'possible_winners', 'duration', 'created_at', 'ended']
    list_display = ['id', 'guild_id', 'prize', 'entries', 'winners', 'possible_winners', 'duration', 'created_at', 'ended']

admin.site.register(Giveaway, GiveawayAdmin)