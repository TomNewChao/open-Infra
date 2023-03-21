# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 16:40
# @Author  : Tom_zc
# @FileName: alarm.py
# @Software: PyCharm

from alarm.resources.alarm_module.alarm_code import AlarmCode
from open_infra.utils.utils_alarm import ActiveAlarmBase


class ResourceUtilizationAlarm(ActiveAlarmBase):
    @classmethod
    def get_alarm_info(cls, name):
        """get alarm info, Overload the method of ActiveAlarmBase"""
        alarm_info_dict = {
            "alarm_id": AlarmCode.TOOLS_NODE_RESOURCE_UTILIZATION_LOW,
            "des_var": [name],
        }
        return alarm_info_dict
