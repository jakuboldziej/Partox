from rest_framework import serializers
from .models import Ticket, Giveaway

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        # fields = ('id', 'closed', 'users')
        fields = '__all__'

class GiveawaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Giveaway
        # fields = ('id', 'closed', 'users')
        fields = '__all__'