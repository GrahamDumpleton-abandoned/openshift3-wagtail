"""
WSGI config for wagtaildemo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtaildemo.settings")

application = get_wsgi_application()

try:
    import mod_wsgi
    from . import metrics
    metrics.initialize()

except ImportError:
    pass
