from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

import requests
import os
from dotenv import load_dotenv

from .models import Settings
from .serializers import SettingsSerializer

load_dotenv()

@login_required()
def home(request):
    user = request.user

    context = {
        'user': user    
    }
    return render(request, "index.html", context)

def loginView(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        return render(request, "login.html")

# discord auth

auth_url_discord = "https://discord.com/api/oauth2/authorize?client_id=979091562724200569&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Foauth2%2Flogin%2Fredirect&response_type=code&scope=identify%20guilds"
auth_url_discord_homeserver = "https://discord.com/api/oauth2/authorize?client_id=979091562724200569&redirect_uri=http%3A%2F%2F188.122.23.154%2Foauth2%2Flogin%2Fredirect&response_type=code&scope=identify%20guilds"

def discord_login(request):
    return redirect(auth_url_discord)

def discord_login_redirect(request):
    code = request.GET.get('code')
    user = exchange_code(code)

    discord_user = authenticate(request, user=user)
    
    try:
        discord_user = list(discord_user)[0]
    except:
        discord_user = discord_user
    
    login(request, discord_user, backend='website.auth.DiscordAuthenticationBackend')

    return redirect("/")

def exchange_code(code):
    # .ENV
    data = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/oauth2/login/redirect", # zmienić na 188
        "scope": "identify, guilds",
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    credentials = response.json()

    access_token = credentials['access_token']
    response = requests.get('https://discord.com/api/v6/users/@me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    user = response.json()
    print(user)
    return user