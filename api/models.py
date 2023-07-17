from django.db import models
from datetime import datetime

class Ticket(models.Model):
    guild_id = models.IntegerField()
    users = models.JSONField()
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)

class Giveaway(models.Model):
    guild_id = models.IntegerField()
    prize = models.CharField(max_length=1000)
    entries = models.JSONField(null=True)
    winners = models.JSONField(null=True)
    possible_winners = models.IntegerField()
    duration = models.DateTimeField(default=datetime.now)
    created_at = models.DateTimeField(default=datetime.now)
    ended = models.BooleanField()