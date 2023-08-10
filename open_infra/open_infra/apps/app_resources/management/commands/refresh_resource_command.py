# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 15:43
# @Author  : Tom_zc
# @FileName: refresh_resource_command.py
# @Software: PyCharm

from django.core.management.base import BaseCommand

from app_resources.resources.init_task import InitMgr


# every day 0:00
class Command(BaseCommand):
    def handle(self, *args, **options):
        print("-" * 25 + "start to refresh app resources" + "-" * 25)
        InitMgr.refresh_account_info()
        InitMgr.refresh_eip()
        InitMgr.refersh_service_sla()
        InitMgr.refresh_service_swr()
        print("-" * 25 + "end to refresh app resources" + "-" * 25)
