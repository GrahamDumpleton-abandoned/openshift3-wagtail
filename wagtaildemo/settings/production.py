from .base import *


DEBUG = False

try:
    from .local import *
except ImportError:
    pass

import os
import dj_database_url

ALLOWED_HOSTS = ['*']

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DATABASES['default'] = dj_database_url.config(conn_max_age=600)
