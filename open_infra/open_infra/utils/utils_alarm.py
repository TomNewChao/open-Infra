# -*- coding: utf-8 -*-
# @Time    : 2022/10/29 14:41
# @Author  : Tom_zc
# @FileName: utils_alarm.py
# @Software: PyCharm
from alarm.resources.alarm_module.alarm_thread import active_alarm


class ActiveAlarmBase(object):
    """Actively trigger the alarm module"""

    @classmethod
    def get_alarm_info(cls, *args, **kwargs):
        """alarm_info_dict = {
            "alarm_id": AlarmCode.MONITOR_DESC_CODE_NODE_CPU_OVERFLOW,
            "des_var": ["hwstaff_hongkong_node10", "{}%".format(80)],
         }
        """
        raise NotImplemented

    @classmethod
    def active_alarm(cls, *args, **kwargs):
        """Actively trigger an alarm"""
        alarm_info = cls.get_alarm_info(*args, **kwargs)
        active_alarm({'alarm_type': True, 'alarm_info_dict': alarm_info})

    @classmethod
    def recover_alarm(cls, *args, **kwargs):
        """Actively trigger an alarm"""
        alarm_info = cls.get_alarm_info(*args, **kwargs)
        active_alarm({'alarm_type': False, 'alarm_info_dict': alarm_info})