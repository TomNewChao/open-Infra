from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler


class AppResourcesConfig(AppConfig):
    name = 'app_resources'
    _scheduler = BackgroundScheduler()
