from .base import *


DEBUG = False

try:
    from .local import *
except ImportError:
    pass


import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['*']

if os.environ.get('OPENSHIFT_MYSQL_DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('OPENSHIFT_MYSQL_DB_NAME'),
            'USER': os.environ.get('OPENSHIFT_MYSQL_DB_USERNAME'),
            'PASSWORD': os.environ.get('OPENSHIFT_MYSQL_DB_PASSWORD'),
            'HOST': os.environ.get('OPENSHIFT_MYSQL_DB_HOST'),
            'PORT': os.environ.get('OPENSHIFT_MYSQL_DB_PORT')
        }
    }
elif os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('OPENSHIFT_POSTGRESQL_DB_NAME'),
            'USER': os.environ.get('OPENSHIFT_POSTGRESQL_DB_USERNAME'),
            'PASSWORD': os.environ.get('OPENSHIFT_POSTGRESQL_DB_PASSWORD'),
            'HOST': os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST'),
            'PORT': os.environ.get('OPENSHIFT_POSTGRESQL_DB_PORT')
        }
    }

if os.environ.get('OPENSHIFT_REDIS_HOST'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://%s:%s/%s' % (
                    os.environ.get('OPENSHIFT_REDIS_HOST'),
                    os.environ.get('OPENSHIFT_REDIS_PORT'),
                    os.environ.get('OPENSHIFT_REDIS_DB_NUMBER', '0')),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
