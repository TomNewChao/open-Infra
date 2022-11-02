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
        from clouds_tools.resources.scan_thread import ScanToolsOnceJobThread, ScanToolsCronJobRefreshDataThread, ScanToolsCronJobScanThread, ScanToolsIntervalJobScanThread
        if settings.IS_RUNSERVER and not settings.DEBUG:
            cls._scheduler.add_job(ScanToolsOnceJobThread.once_job, "date", run_date=datetime.datetime.now())
            cls._scheduler.add_job(ScanToolsCronJobRefreshDataThread.immediately_cron_job, "cron", hour='0', next_run_time=datetime.datetime.now())
            cls._scheduler.add_job(ScanToolsCronJobScanThread.cron_job, "cron", hour='1')
            cls._scheduler.add_job(ScanToolsIntervalJobScanThread.interval_job, "interval", hours=1)
            # cls._scheduler.add_job(ScanToolsIntervalJobScanThread.interval_job, "interval", seconds=30, next_run_time=datetime.datetime.now())
            cls._scheduler.start()

    @runserver_executor
    def ready(self):
        self._start_thread()
