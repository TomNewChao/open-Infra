# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 10:44
# @Author  : Tom_zc
# @FileName: apps.py
# @Software: PyCharm
from django.apps import AppConfig
from django.conf import settings
from open_infra.utils.common import runserver_executor


class AlarmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alarm'

    @runserver_executor
    def ready(self):
        from alarm.resources.alarm_module.alarm_thread import AlarmClient
        if settings.IS_COLLECT_ALARM:
            alarm_client = AlarmClient()
            alarm_client.start()
