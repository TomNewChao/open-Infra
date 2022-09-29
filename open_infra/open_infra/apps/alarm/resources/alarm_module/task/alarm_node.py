# -*- coding: utf-8 -*-
# @Time    : 2022/9/19 14:31
# @Author  : Tom_zc
# @FileName: alarm_node.py
# @Software: PyCharm

import logging
import time

from django.conf import settings

from alarm.resources.alarm_handler import AlarmBaseHandler, AlarmHandlerConfig
from alarm.resources.alarm_module.alarm_code import AlarmCode, AlarmName
from alarm.resources.alarm_module.alarm_thread import batch_recover_faded_alarm, active_alarm
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
        alarm_name = AlarmName.get_alarm_name_by_id(AlarmName.NAME_NODE_CPU)
        alarm_list_data, alarm_md5_data = AlarmBaseHandler.get_node_alarm_info(query, alarm_threshold, alarm_code)
        active_alarm(alarm_list_data)
        batch_recover_faded_alarm(alarm_name, alarm_md5_data)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def mem_alarm(self):
        """节点内存定时报警"""
        query = AlarmHandlerConfig.node_mem_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_ECS_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_NODE_MEM_OVERFLOW
        alarm_name = AlarmName.get_alarm_name_by_id(AlarmName.NAME_NODE_MEM)
        alarm_list_data, alarm_md5_data = AlarmBaseHandler.get_node_alarm_info(query, alarm_threshold, alarm_code)
        active_alarm(alarm_list_data)
        batch_recover_faded_alarm(alarm_name, alarm_md5_data)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def fs_alarm(self):
        """节点文件容量报警"""
        query = AlarmHandlerConfig.node_fs_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_ECS_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_NODE_DISK_OVERFLOW
        alarm_name = AlarmName.get_alarm_name_by_id(AlarmName.NAME_NODE_DISK)
        alarm_list_data, alarm_md5_data = AlarmBaseHandler.get_node_alarm_info(query, alarm_threshold, alarm_code)
        active_alarm(alarm_list_data)
        batch_recover_faded_alarm(alarm_name, alarm_md5_data)
