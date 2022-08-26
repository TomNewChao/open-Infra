import datetime
from django.apps import AppConfig
from open_infra.utils.common import runserver_executor
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings


class CloudsToolsConfig(AppConfig):
    name = 'clouds_tools'
    _scheduler = BackgroundScheduler()

    @classmethod
    def _start_thread(cls):
        from clouds_tools.resources.scan_thread import ScanToolsThread
        if settings.IS_RUNSERVER:
            cls._scheduler.add_job(ScanToolsThread.once_job, 'date', run_date=datetime.datetime.now())
            cls._scheduler.add_job(ScanToolsThread.cron_job, 'cron', hour='0', next_run_time=datetime.datetime.now())
            cls._scheduler.start()

    @runserver_executor
    def ready(self):
        self._start_thread()
