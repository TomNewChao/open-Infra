import datetime
from django.apps import AppConfig
from open_infra.utils.common import runserver_executor
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings


class AppResourcesConfig(AppConfig):
    name = 'app_resources'
    _scheduler = BackgroundScheduler()

    @classmethod
    def _start_thread(cls):
        from app_resources.resources.init_task import InitMgr
        if not settings.DEBUG:
            InitMgr.immediately_task()
            cls._scheduler.add_job(InitMgr.crontab_task, "cron", hour='0')
            cls._scheduler.start()
        elif settings.IS_COLLECT_APP_RES:
            InitMgr.test_task()
            pass

    @runserver_executor
    def ready(self):
        self._start_thread()
