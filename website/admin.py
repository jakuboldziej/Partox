from django.contrib import admin

from .models import DiscordUser

class DiscordUserAdmin(admin.ModelAdmin):
    fields = ['id', 'username', 'avatar', 'public_flags', 'flags', 'locale', 'mfa_enabled', 'last_login', 'is_active', 'guilds']
    list_display = ['id', 'username', 'avatar', 'public_flags', 'flags', 'locale', 'mfa_enabled', 'last_login', 'is_active', 'guilds']
admin.site.register(DiscordUser, DiscordUserAdmin)