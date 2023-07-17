from django.urls import path

from . import views

urlpatterns = [
    path('', view=views.index, name="APIindex"),
    path('statistics/', view=views.statistics, name="APIstatistics"),

    # API

    # Tickets
    path('get-tickets/', view=views.get_tickets, name="get_tickets"),
    path('get-ticket/<int:id>', view=views.get_ticket, name="get_ticket"),
    path('create-ticket/', view=views.create_ticket, name="create_ticket"),
    path('open-ticket/<int:id>', view=views.open_ticket, name="open_ticket"),
    path('close-ticket/<int:id>', view=views.close_ticket, name="close_ticket"),
    path('add-user-to-ticket/<int:id>', view=views.add_user_to_ticket, name="add_user_to_ticket"),
    path('remove-user-from-ticket/<int:id>', view=views.remove_user_from_ticket, name="remove_user_from_ticket"),

    # Giveaways
    path('get-giveaways/', view=views.get_giveaways, name="get_giveaways"),
    path('create-giveaway/', view=views.create_giveaway, name="create_giveaway"),
    path('end-giveaway/<int:id>', view=views.end_giveaway, name="end_giveaway"),
    path('add-giveaway-entry/<int:id>', view=views.add_giveaway_entry, name="add_giveaway_entry"),
]
