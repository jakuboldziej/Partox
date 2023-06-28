from django.contrib import admin

from .models import Ticket, Giveaway

class TicketAdmin(admin.ModelAdmin):
    fields = ['users', 'closed', 'guild_id']
    list_display = ['id', 'users', 'closed', 'guild_id']

admin.site.register(Ticket, TicketAdmin)

class GiveawayAdmin(admin.ModelAdmin):
    fields = ['name', 'users', 'guild_id']
    list_display = ['name', 'id', 'users', 'guild_id']

admin.site.register(Giveaway, GiveawayAdmin)