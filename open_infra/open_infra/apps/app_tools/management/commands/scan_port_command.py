# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 15:03
# @Author  : Tom_zc
# @FileName: scan_port_command.py
# @Software: PyCharm
from django.core.management.base import BaseCommand
from app_tools.resources.init_task import InitMgr


# every day 1:00
class Command(BaseCommand):
    def handle(self, *args, **options):
        print("-" * 25 + "start to scan port and obs" + "-" * 25)
        InitMgr.refresh_high_level_port()
        InitMgr.scan_all_task()
        print("-" * 25 + "end to scan port and obs" + "-" * 25)
