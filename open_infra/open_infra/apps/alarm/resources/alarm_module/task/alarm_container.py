# -*- coding: utf-8 -*-
# @Time    : 2022/9/19 14:30
# @Author  : Tom_zc
# @FileName: alarm_container.py
# @Software: PyCharm

import logging
import math
import time
import traceback

from django.conf import settings

from alarm.resources.alarm_handler import AlarmBaseHandler, AlarmHandlerConfig
from alarm.resources.alarm_module.alarm_code import AlarmCode
from alarm.resources.alarm_module.task import BaseAlarm, AlarmTask

logger = logging.getLogger("django")


class ContainerAlarm(BaseAlarm):
    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def cpu_alarm(self):
        """容器cpu定时报警"""
        query = AlarmHandlerConfig.container_cpu_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_CCE_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_CONTAINER_CPU_OVERFLOW
        return AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def mem_alarm(self):
        """容器内存定时报警"""
        query = AlarmHandlerConfig.container_mem_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_CCE_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_CONTAINER_MEM_OVERFLOW
        return AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def fs_alarm(self):
        """容器文件容量报警"""
        query = AlarmHandlerConfig.container_fs_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_CCE_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_CONTAINER_DISK_OVERFLOW
        return AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)
