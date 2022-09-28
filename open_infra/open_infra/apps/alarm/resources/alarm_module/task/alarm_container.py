# -*- coding: utf-8 -*-
# @Time    : 2022/9/19 14:30
# @Author  : Tom_zc
# @FileName: alarm_container.py
# @Software: PyCharm

import logging
import time

from django.conf import settings

from alarm.resources.alarm_handler import AlarmBaseHandler, AlarmHandlerConfig
from alarm.resources.alarm_module.alarm_code import AlarmCode, AlarmName
from alarm.resources.alarm_module.task import BaseAlarm, AlarmTask
from alarm.resources.alarm_module.alarm_thread import active_alarm, batch_recover_faded_alarm

logger = logging.getLogger("django")


class ContainerAlarm(BaseAlarm):
    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def cpu_alarm(self):
        """容器cpu定时报警"""
        query = AlarmHandlerConfig.container_cpu_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_CCE_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_CONTAINER_CPU_OVERFLOW
        alarm_name = AlarmName.get_alarm_name_by_id(AlarmName.NAME_CONTAINER_CPU)
        alarm_list_data, alarm_md5_data = AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)
        active_alarm(alarm_list_data)
        batch_recover_faded_alarm(alarm_name, alarm_md5_data)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def mem_alarm(self):
        """容器内存定时报警"""
        query = AlarmHandlerConfig.container_mem_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_CCE_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_CONTAINER_MEM_OVERFLOW
        alarm_name = AlarmName.get_alarm_name_by_id(AlarmName.NAME_CONTAINER_MEM)
        alarm_list_data, alarm_md5_data = AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)
        active_alarm(alarm_list_data)
        batch_recover_faded_alarm(alarm_name, alarm_md5_data)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def fs_alarm(self):
        """容器文件容量报警"""
        query = AlarmHandlerConfig.container_fs_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_CCE_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_CONTAINER_DISK_OVERFLOW
        alarm_name = AlarmName.get_alarm_name_by_id(AlarmName.NAME_CONTAINER_DISK)
        alarm_list_data, alarm_md5_data = AlarmBaseHandler.get_container_alarm_info(query, alarm_threshold, alarm_code)
        active_alarm(alarm_list_data)
        batch_recover_faded_alarm(alarm_name, alarm_md5_data)

    @BaseAlarm.add()
    @AlarmTask(exec_interval=2 * 60)
    def res_count_alarm(self):
        """容器文件容量报警"""
        query = AlarmHandlerConfig.container_fs_query.format(settings.ALARM_PROMETHEUS_URL, int(time.time()))
        alarm_threshold = settings.ALARM_RES_COUNT_THRESHOLD
        alarm_code = AlarmCode.MONITOR_DESC_CODE_CONTAINER_REST_COUNT_OVERFLOW
        alarm_list_data = AlarmBaseHandler.get_container_count_info(query, alarm_threshold, alarm_code)
        active_alarm(alarm_list_data)
