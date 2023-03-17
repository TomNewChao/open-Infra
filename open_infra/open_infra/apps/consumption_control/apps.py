import datetime
from django.apps import AppConfig
from open_infra.utils.common import runserver_executor
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings


class ConsumptionControlConfig(AppConfig):
    name = 'consumption_control'
    _scheduler = BackgroundScheduler()

    @classmethod
    def _start_thread(cls):
        from consumption_control.resources.init_task import InitMgr
        if not settings.DEBUG:
            InitMgr.immediately_task()
            cls._scheduler.add_job(InitMgr.crontab_task, "cron", hour='2')
            cls._scheduler.add_job(InitMgr.crontab_task_week, "cron", day_of_week='1', hour=3, minute=0, second=0)
            cls._scheduler.start()
        elif settings.IS_COLLECT_CONSUMPTION_CON:
            InitMgr.test_task()
            pass

    @runserver_executor
    def ready(self):
        self._start_thread()
