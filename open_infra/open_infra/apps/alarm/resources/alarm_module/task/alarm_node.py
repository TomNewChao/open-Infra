# -*- coding: utf-8 -*-
# @Time    : 2022/9/19 14:31
# @Author  : Tom_zc
# @FileName: alarm_node.py
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


class NodeAlarm(BaseAlarm):
    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def cpu_alarm(self):
        """节点cpu定时报警"""
        query = AlarmHandlerConfig.node_cpu_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_ECS_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_NODE_CPU_OVERFLOW
        return AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def mem_alarm(self):
        """节点内存定时报警"""
        query = AlarmHandlerConfig.node_mem_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_ECS_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_NODE_MEM_OVERFLOW
        return AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def fs_alarm(self):
        """节点文件容量报警"""
        query = AlarmHandlerConfig.node_fs_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_ECS_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_NODE_DISK_OVERFLOW
        return AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)
