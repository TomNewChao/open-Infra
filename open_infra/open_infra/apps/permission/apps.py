# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 10:44
# @Author  : Tom_zc
# @FileName: apps.py
# @Software: PyCharm

import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from open_infra.utils.common import runserver_executor
from django.conf import settings


class PermissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permission'
    _permission_scheduler = BackgroundScheduler()

    @classmethod
    def _start_thread(cls):
        from permission.resources.permission_thread import KubeconfigClearExpiredThread
        if not settings.DEBUG:
            cls._permission_scheduler.add_job(KubeconfigClearExpiredThread.cron_job, 'interval', minutes=10)
            cls._permission_scheduler.start()
        elif settings.IS_COLLECT_PERMISSION:
            KubeconfigClearExpiredThread.clear_expired_data()
            pass

    @runserver_executor
    def ready(self):
        self._start_thread()
