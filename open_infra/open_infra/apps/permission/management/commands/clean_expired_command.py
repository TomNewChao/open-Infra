# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 19:31
# @Author  : Tom_zc
# @FileName: clean_expired_command.py
# @Software: PyCharm


from django.core.management.base import BaseCommand
from permission.resources.permission_thread import KubeconfigClearExpiredThread


# every 10 minutes
class Command(BaseCommand):
    def handle(self, *args, **options):
        print("-" * 25 + "start to clean expired data" + "-" * 25)
        KubeconfigClearExpiredThread.clear_expired_data()
        print("-" * 25 + "end to clean expired data" + "-" * 25)
