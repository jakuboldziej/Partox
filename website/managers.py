from django.contrib.auth import models
from django.contrib.auth.models import User

class DiscordUserOAuth2Manager(models.UserManager):
    def create_new_discord_user(self, user):
        new_user = self.create(
            id=user['id'],
            username=user['username'],
            avatar=user['avatar'],
            public_flags=user['public_flags'],
            flags=user['flags'],
            locale=user['locale'],
            mfa_enabled=user['mfa_enabled'],
        )
        return new_user