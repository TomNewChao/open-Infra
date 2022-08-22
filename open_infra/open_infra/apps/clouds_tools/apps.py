import datetime
from django.apps import AppConfig
from open_infra.utils.common import runserver_executor
from apscheduler.schedulers.background import BackgroundScheduler


class CloudsToolsConfig(AppConfig):
    name = 'clouds_tools'
    _scheduler = BackgroundScheduler()

    @classmethod
    def _start_thread(cls):
        from clouds_tools.resources.scan_thread import ScanToolsThread
        cls._scheduler.add_job(ScanToolsThread.refresh_data, 'cron', hour='0', next_run_time=datetime.datetime.now())
        cls._scheduler.start()

    @runserver_executor
    def ready(self):
        self._start_thread()
