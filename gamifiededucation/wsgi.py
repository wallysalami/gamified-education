"""
WSGI config for gamifiededucation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise
from gamifiededucation.helper import load_to_environment

base_dir = os.path.dirname(os.path.abspath(__file__))
local_env_path = os.path.join(base_dir, '../local.env')
load_to_environment(local_env_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gamifiededucation.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
