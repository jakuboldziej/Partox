from django.db import models

# Create your models here.
class Ticket(models.Model):
    # users = models.TextField(max_length=10000)
    guild_id = models.IntegerField()
    users = models.JSONField()
    closed = models.BooleanField(default=False)

class Giveaway(models.Model):
    guild_id = models.IntegerField()
    name = models.CharField(max_length=100, default="")
    # users = models.TextField(max_length=10000)
    users = models.JSONField()
