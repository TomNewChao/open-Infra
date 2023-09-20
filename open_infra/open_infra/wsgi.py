"""
WSGI config for open_infra project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from alarm.resources.alarm_module.alarm_thread import AlarmClient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'open_infra.settings.prod')

# Pull up the alarm thread
print("-" * 25 + "start to alarm" + "-" * 25)
alarm_client = AlarmClient()
alarm_client.start()
print("-" * 25 + "start to wsgi" + "-" * 25)
application = get_wsgi_application()
