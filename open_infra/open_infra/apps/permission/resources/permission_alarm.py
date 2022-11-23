# -*- coding: utf-8 -*-
# @Time    : 2022/11/17 15:40
# @Author  : Tom_zc
# @FileName: permission_alarm.py
# @Software: PyCharm
from alarm.resources.alarm_module.alarm_code import AlarmCode
from open_infra.utils.utils_alarm import ActiveAlarmBase


class KubeconfigAlarm(ActiveAlarmBase):
    @classmethod
    def get_alarm_info(cls, username):
        """get alarm info, Overload the method of ActiveAlarmBase"""
        alarm_info_dict = {
            "alarm_id": AlarmCode.PERMISSION_APPLY_KUBECONFIG_FAILED,
            "des_var": [username, ],
        }
        return alarm_info_dict
