# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 15:59
# @Author  : Tom_zc
# @FileName: refresh_refresh_resource_command.py
# @Software: PyCharm

from django.core.management.base import BaseCommand
from consumption_control.resources.init_task import InitMgr


# every week 3:00
class Command(BaseCommand):
    def handle(self, *args, **options):
        print("-" * 25 + "start to refresh bill" + "-" * 25)
        InitMgr.refresh_resource_utilization()
        print("-" * 25 + "end to refresh bill" + "-" * 25)
