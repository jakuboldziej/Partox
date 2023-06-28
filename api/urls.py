from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', view=views.index, name="APIindex"),
    path('statistics/', view=views.statistics, name="APIstatistics"),

    # API
    path('get-tickets/', view=views.get_tickets, name="get_tickets"),
    path('get-ticket/<int:id>', view=views.get_ticket, name="get_ticket"),
    path('open-ticket/<int:id>', view=views.open_ticket, name="open_ticket"),
    path('close-ticket/<int:id>', view=views.close_ticket, name="close_ticket"),
    path('create-ticket/', view=views.create_ticket, name="create_ticket"),
    path('add-user-to-ticket/<int:id>', view=views.add_user_to_ticket, name="add_user_to_ticket"),
    path('remove-user-from-ticket/<int:id>', view=views.remove_user_from_ticket, name="remove_user_from_ticket"),
]
