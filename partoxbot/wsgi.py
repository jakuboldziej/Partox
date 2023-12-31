import os

from django.core.wsgi import get_wsgi_application

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'partoxbot.settings')

application = get_wsgi_application()
