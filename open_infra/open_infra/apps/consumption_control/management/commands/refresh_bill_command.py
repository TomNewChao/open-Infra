# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 15:52
# @Author  : Tom_zc
# @FileName: refresh_bill_command.py
# @Software: PyCharm


from django.core.management.base import BaseCommand
from consumption_control.resources.init_task import InitMgr


# month day0 2:00
class Command(BaseCommand):
    def handle(self, *args, **options):
        print("-" * 25 + "start to refresh bill" + "-" * 25)
        InitMgr.refresh_bill_info()
        print("-" * 25 + "end to refresh bill" + "-" * 25)
