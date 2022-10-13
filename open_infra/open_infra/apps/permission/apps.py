# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 10:44
# @Author  : Tom_zc
# @FileName: apps.py
# @Software: PyCharm

import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from open_infra.utils.common import runserver_executor


class PermissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permission'
    _permission_scheduler = BackgroundScheduler()

    @classmethod
    def _start_thread(cls):
        from permission.resources.permission_thread import KubeconfigClearExpiredThread
        cls._permission_scheduler.add_job(KubeconfigClearExpiredThread.immediately_cron_job, 'cron', hour='0', next_run_time=datetime.datetime.now())
        cls._permission_scheduler.add_job(KubeconfigClearExpiredThread.cron_job, 'interval', minutes=10)
        cls._permission_scheduler.start()

    @runserver_executor
    def ready(self):
        self._start_thread()
