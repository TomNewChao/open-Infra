# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: apps.py
# @Software: PyCharm

import datetime
from django.apps import AppConfig
from open_infra.utils.common import runserver_executor
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings


class CloudsToolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clouds_tools'
    _scheduler = BackgroundScheduler()

    @classmethod
    def _start_thread(cls):
        from clouds_tools.resources.init_task import InitMgr
        if not settings.DEBUG:
            InitMgr.immediately_task()
            cls._scheduler.add_job(InitMgr.crontab_task, "cron", hour='1')
            cls._scheduler.start()
        elif settings.IS_COLLECT_CLOUDS_TOOLS:
            InitMgr.test_task()

    @runserver_executor
    def ready(self):
        self._start_thread()
