from django.contrib import admin

from .models import Settings

class SettingsAdmin(admin.ModelAdmin):
    fields = ('prefix',)
    list_display = ['prefix', ]
admin.site.register(Settings, SettingsAdmin)