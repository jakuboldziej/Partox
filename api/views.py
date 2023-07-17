from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TicketSerializer, GiveawaySerializer
from .models import Ticket, Giveaway

# Create your views here.
def index(request):
    ticket_count: int = Ticket.objects.all().count()    
    giveaway_count: int = Giveaway.objects.all().count()    

    requests = ticket_count + giveaway_count

    context = {
        'requests': requests,
    }
    return render(request, "api/index.html", context)

def statistics(request):
    return render(request, "api/statistics.html")

# API

# Tickets
@api_view(['GET'])
def get_tickets(request):
    tickets = Ticket.objects.all()
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_ticket(request, id):
    ticket = Ticket.objects.get(id=id)
    serializer = TicketSerializer(ticket, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def create_ticket(request):
    serializer = TicketSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
def open_ticket(request, id):
    ticket = Ticket.objects.get(id=id)
    serializer = TicketSerializer(instance=ticket, data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['POST'])
def close_ticket(request, id):
    ticket = Ticket.objects.get(id=id)
    serializer = TicketSerializer(instance=ticket, data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['POST'])
def add_user_to_ticket(request, id):
    ticket = Ticket.objects.get(id=id)
    serializer = TicketSerializer(instance=ticket, data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['POST'])
def remove_user_from_ticket(request, id):
    ticket = Ticket.objects.get(id=id)
    serializer = TicketSerializer(instance=ticket, data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

# Giveaways
@api_view(['GET'])
def get_giveaways(request):
    giveaways = Giveaway.objects.all()
    serializer = GiveawaySerializer(giveaways, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_giveaway(request):
    serializer = GiveawaySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    
    return Response(serializer.data)

@api_view(['POST'])
def end_giveaway(request, id):
    giveaway = Giveaway.objects.get(id=id)
    serializer = GiveawaySerializer(instance=giveaway, data=request.data)
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
    return Response(serializer.data)

@api_view(['POST'])
def add_giveaway_entry(request, id):
    giveaway = Giveaway.objects.get(id=id)
    serializer = GiveawaySerializer(instance=giveaway, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)