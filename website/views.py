from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

import requests
import os
from dotenv import load_dotenv

from api.models import Ticket, Giveaway
# from .serializers import SettingsSerializer

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# 404 Handling
def view_page_not_found(request):
    return render(request, '404.html')

# Views

@login_required()
def home(request):
    user = request.user

    context = {
        'user': user    
    }
    return render(request, "index.html", context)

def docs(request):
    return render(request, "docs.html")

@login_required()
def manage_servers(request):
    sync_guilds(request)
    guilds = request.session['guilds']
    shared_guilds = guilds[0]
    admin_guilds = [guild for guild in guilds[1] if guild not in shared_guilds]

    context = {
        'shared_guilds': shared_guilds,
        'admin_guilds': admin_guilds
    }
    return render(request, "manage_servers.html", context)
    
def dashboard(request, guild_id):
    guilds = request.session['guilds'][0]

    guild = next(guild for guild in guilds if int(guild['id']) == guild_id)
    guildInfo = getGuildInfo(guild_id)

    guild['members'] = len(guildInfo[0]) - len(guildInfo[2])
    guild['channels'] = len(guildInfo[1])
    guild['bots'] = len(guildInfo[2])

    tickets = Ticket.objects.filter(guild_id=guild_id)
    giveaways = Giveaway.objects.filter(guild_id=guild_id)

    context = {
        'tickets': tickets,
        'giveaways': giveaways,
        'guild': guild
    }
    return render(request, "dashboard.html", context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        return render(request, "login.html")

def sync_guilds(request):
    credentials = {'access_token': request.user.access_token} 
    data = manageGuilds(credentials)
    request.session['guilds'] = data[1]

    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

# Discord Auth

auth_url_discord_localhost = os.getenv("AUTH_URL_DISCORD_LOCALHOST")
auth_url_discord_homeserver_8080 = os.getenv("AUTH_URL_DISCORD_HOMESERVER_8080")
auth_url_discord_homeserver_8000 = os.getenv("AUTH_URL_DISCORD_HOMESERVER_8000")
auth_url_no_ip = os.getenv("AUTH_URL_NO_IP")

def discord_login(request):
    # return redirect(auth_url_discord_homeserver_8080)
    return redirect(auth_url_discord_localhost)

def discord_login_redirect(request):
    code = request.GET.get('code')
    data = exchange_code(code)
    request.session['guilds'] = data[1]
    
    discord_user = authenticate(request, user=data[0])
    
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
        "redirect_uri": "http://localhost:8000/oauth2/login/redirect", 
        # "redirect_uri": "http://partox.ddns.net/oauth2/login/redirect", 
        # "redirect_uri": "http://188.122.23.154:8080/oauth2/login/redirect",
        "scope": "guilds, identify",
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    credentials = response.json()

    user, guilds = manageGuilds(credentials)

    return [user, guilds]

def manageGuilds(credentials):
    access_token = credentials['access_token']

    user = requests.get('https://discord.com/api/v6/users/@me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    user = user.json()
    user['access_token'] = access_token

    user_guilds = requests.get('https://discord.com/api/v6/users/@me/guilds', headers={
        'Authorization': f'Bearer {access_token}'
    })
    user_guilds = user_guilds.json()

    token = os.getenv("TOKEN")
    bot_guilds = requests.get('https://discord.com/api/v6/users/@me/guilds', headers={
        'Authorization': f'Bot {token}'
    })
    bot_guilds = bot_guilds.json()

    shared_guilds = [guild for guild in user_guilds if guild['id'] in map(lambda i: i['id'], bot_guilds) and (guild['permissions'] & 0x8) == 0x8]
    admin_guilds = [guild for guild in user_guilds if (guild['permissions'] & 0x8) == 0x8]

    guilds = [shared_guilds, admin_guilds]

    return user, guilds

def getGuildInfo(guild_id):
    members = requests.get(f'https://discordapp.com/api/v6/guilds/{str(guild_id)}/members?limit=1000', headers={
        'Authorization': f'Bot {os.getenv("TOKEN")}'
    })
    members = members.json()
    bots = [member for member in members if 'bot' in member['user'].keys()]

    channels = requests.get(f'https://discordapp.com/api/v6//guilds/{str(guild_id)}/channels', headers={
        'Authorization': f'Bot {os.getenv("TOKEN")}'
    })
    channels = channels.json()

    return [members, channels, bots]