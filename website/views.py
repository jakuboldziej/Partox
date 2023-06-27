from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

import requests
import os
from dotenv import load_dotenv

# from .serializers import SettingsSerializer

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Views

@login_required()
def home(request):
    user = request.user

    context = {
        'user': user    
    }
    return render(request, "index.html", context)

@login_required()
def manage_servers(request):
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

    context = {
        'guild': guild
    }
    return render(request, "dashboard.html", context)

def bot_status(request):
    url = "https://api.uptimerobot.com/v2/getMonitors"
            
    payload = f"api_key={os.getenv('API_KEY')}&format=json&logs=1"
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
        }
            
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response)
    response = response.json()

    monitor = response['monitors'][0]
    print(monitor['logs'])

    context = {
        'monitor': monitor
    }
    return render(request, "bot_status.html", context)

def loginView(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        return render(request, "login.html")

# Discord Auth

auth_url_discord_localhost = "https://discord.com/api/oauth2/authorize?client_id=979091562724200569&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Foauth2%2Flogin%2Fredirect&response_type=code&scope=identify%20guilds"
auth_url_discord_homeserver_8080 = "https://discord.com/api/oauth2/authorize?client_id=979091562724200569&redirect_uri=http%3A%2F%2F188.122.23.154%3A8080%2Foauth2%2Flogin%2Fredirect&response_type=code&scope=identify%20guilds"
auth_url_discord_homeserver_8000 = "https://discord.com/api/oauth2/authorize?client_id=979091562724200569&redirect_uri=http%3A%2F%2F188.122.23.154%3A8000%2Foauth2%2Flogin%2Fredirect&response_type=code&scope=identify%20guilds"
auth_url_no_ip = "https://discord.com/api/oauth2/authorize?client_id=979091562724200569&redirect_uri=http%3A%2F%2Fpartox.ddns.net%2Foauth2%2Flogin%2Fredirect&response_type=code&scope=identify%20guilds"

def discord_login(request):
    # return redirect(auth_url_discord_homeserver_8080)
    return redirect(auth_url_no_ip)

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
        # "redirect_uri": "http://localhost:8000/oauth2/login/redirect", 
        "redirect_uri": "https://partox.ddns.net/oauth2/login/redirect", 
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