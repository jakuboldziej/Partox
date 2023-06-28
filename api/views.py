from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

from .serializers import TicketSerializer
from .models import Ticket

# Create your views here.
def index(request):
    return render(request, "api/index.html")

def statistics(request):
    return render(request, "api/statistics.html")

# API
@api_view(['GET'])
def get_tickets(request):
    tickets = Ticket.objects.all()
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_ticket(request, id):
    tickets = Ticket.objects.get(id=id)
    serializer = TicketSerializer(tickets, many=False)
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