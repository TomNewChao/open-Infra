# -*- coding: utf-8 -*-
# @Time    : 2022/11/17 14:06
# @Author  : Tom_zc
# @FileName: clouds_tools_alarm.py
# @Software: PyCharm
from alarm.resources.alarm_module.alarm_code import AlarmCode
from open_infra.utils.utils_alarm import ActiveAlarmBase


class CloudsToolsAlarm(ActiveAlarmBase):
    @classmethod
    def get_alarm_info(cls):
        """get alarm info, Overload the method of ActiveAlarmBase"""
        alarm_info_dict = {
            "alarm_id": AlarmCode.TOOLS_NODE_HIGH_RISK_PORT,
            "des_var": [],
        }
        return alarm_info_dict
