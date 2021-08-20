"""
WSGI config for woningzoeker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from woningzoeker.sentry import initialize_sentry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'woningzoeker.settings.production')

application = get_wsgi_application()

initialize_sentry()
