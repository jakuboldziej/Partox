from django.db import models
from .managers import DiscordUserOAuth2Manager

class DiscordUser(models.Model):
    objects = DiscordUserOAuth2Manager()

    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=200)
    avatar = models.CharField(max_length=100)
    public_flags = models.IntegerField()
    flags = models.IntegerField()
    locale = models.CharField(max_length=100)
    mfa_enabled = models.BooleanField()
    last_login = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    access_token = models.CharField(max_length=1000)
    guilds = models.JSONField(null=True)

    def is_authenticated(self):
        return True