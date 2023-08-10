# -*- coding: utf-8 -*-

import logging
import time
import traceback

from alarm.resources.alarm_module.alarm_code import AlarmCode
from alarm.resources.alarm_module.alarm_thread import active_alarm
from alarm.resources.alarm_module.constants import AlarmType
from alarm.resources.alarm_module.task import BaseAlarm, AlarmTask

logger = logging.getLogger("alarm")


class DemoAlarm(BaseAlarm):
    """报警的三种形式：
    1.框架定时报警， 可以使用alarm方法，或任意方法使用BaseAlarm.add()进行装饰，返回报警信息，如果没有报警则返回为None
    2.主动报警， 直接调用 active_alarm 方法进行报警
    3.框架定时主动报警， 结合1+2使用
    """

    def __init__(self):
        pass

    # @AlarmTask(exec_interval=1 * 30)
    # def alarm(self):
    #     """框架定时报警1"""
    #     alarm_info_dict = {
    #         "alarm_type": AlarmType.ALARM,
    #         "alarm_info_dict": {
    #             "alarm_id": AlarmCode.MONITOR_DESC_CODE_NODE_CPU_OVERFLOW,
    #             "des_var": ["hwstaff_hongkong_node10", "{}%".format(80)],
    #         }
    #     }
    #     return alarm_info_dict
    #
    # @BaseAlarm.add()
    # @AlarmTask(exec_interval=60 * 60)
    # def alarm_demo1(self):
    #     """框架定时报警2"""
    #     return dict()
    #
    # def alarm_demo2(self):
    #     """主动报警"""
    #     # active_alarm({'alarm_type': True, 'val_dict': {}})
    #     pass
    #
    # @BaseAlarm.add()
    # @AlarmTask(exec_interval=60 * 60, is_active=False)
    # def alarm_demo3(self):
    #     '''框架定时主动报警'''
    #     # active_alarm({'alarm_type': True, 'val_dict': {}})
    #     pass
