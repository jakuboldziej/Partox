from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginView, name='login'),
    path('manage-servers/', views.manage_servers, name='manage_servers'),
    path('bot-status/', views.bot_status, name='bot_status'),
    path('dashboard/<int:guild_id>', views.dashboard, name='dashboard'),

    path('oauth2/login', views.discord_login, name='oauth2_login'),
    path('oauth2/login/redirect', views.discord_login_redirect, name='oauth2_login_redirect'),

    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name="logout")
]
