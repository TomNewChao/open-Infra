# -*- coding: utf-8 -*-

import os
import sys
import pkgutil
import inspect
import logging
import importlib
from functools import wraps

from alarm.models import Alarm
from alarm.resources.alarm_module.common import calc_next_run_time

logger = logging.getLogger("django")


class BaseAlarm(object):
    _alarm_function = 'alarm'  # 默认告警方法名

    @staticmethod
    def add():
        """注册为报警方法，用于被收集"""

        def _wrapper(func):
            func._resource_function_ = True
            return func

        return _wrapper

    @classmethod
    def endpoints(cls):
        """收集当前资源类的所有注册告警方法对象"""
        result = []
        for _, func in inspect.getmembers(cls, predicate=callable):
            if func.__name__ == cls._alarm_function:
                result.append(func)
            elif hasattr(func, '_resource_function_'):
                result.append(func)
            else:
                continue
        return result

    @staticmethod
    def is_need_recover_alarm(alarm_id):
        """通过判断数据库的状态决定是否需要上报恢复告警"""
        try:
            Alarm.objects.get(alarm_id=alarm_id, is_recover=False)
        except Alarm.DoesNotExist as e:
            logger.info("[is_need_recover_alarm] ")
            return False
        else:
            return True


class AlarmTask:

    def __init__(self, is_active=False, exec_interval=5 * 60, wait_for=45.0, exception_handler=None):
        super(AlarmTask, self).__init__()
        """
        :param is_active: 是否主动上报，默认不主动上报，通过框架上报,主动上报时，框架只负责定时启动函数
        :param exec_interval: 函数执行间隔
        :param wait_for: 超时时长
        :param exception_handler: 异常函数
        """
        self.is_active = is_active
        self.wait_for = wait_for
        self.exec_interval = exec_interval
        self.exception_handler = exception_handler

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from alarm.resources.alarm_module.alarm_thread import TaskManager, AlarmGlobalConfig
            if not AlarmGlobalConfig.REAL_EXECUTION:
                run_time = calc_next_run_time(self.exec_interval)
                func_dict = {'func_obj': func, 'exec_interval': self.exec_interval, 'wait_for': self.wait_for,
                             'run_time': run_time, 'args': args, 'kwargs': kwargs, 'is_active': self.is_active,
                             'run_status': False
                             }
                AlarmGlobalConfig.TASK_LIST.append(func_dict)
            else:
                arg_map_dict = self._gen_arg_map(func, args, kwargs)
                real_arg_dict = {}
                for key, val in list(arg_map_dict.items()):
                    if isinstance(key, str) and key != 'self':
                        real_arg_dict[key] = val
                TaskManager.run(self.exec_interval, self.wait_for, self.is_active, real_arg_dict, func, args, kwargs)

        return wrapper

    @staticmethod
    def _gen_arg_map(func, args, kwargs):
        """获取参数映射关系"""
        arg_map = {}
        if sys.version_info > (3, 0):
            sig = inspect.signature(func)
            arg_list = [a for a in sig.parameters]
        else:
            sig = inspect.getargspec(func)
            arg_list = [a for a in sig.args]

        for idx, arg in enumerate(arg_list):
            if idx < len(args):
                arg_map[arg] = args[idx]
            else:
                if arg in kwargs:
                    arg_map[arg] = kwargs[arg]
            if arg in arg_map:
                arg_map[idx] = arg_map[arg]
        all_arg_len = len(arg_list)
        transmit_arg_len = len(args) + len(kwargs)
        if all_arg_len != transmit_arg_len:
            logger.warning("[_gen_arg_map] Parameter is not standard")
            diff_len = all_arg_len - transmit_arg_len
            initial_index = transmit_arg_len
            defaults = sig.defaults
            if defaults:
                handle_arg_list = arg_list[-diff_len:]
                handle_default_list = defaults[-diff_len:]
                for index, handle_arg in enumerate(handle_arg_list):
                    arg_map[initial_index + index] = handle_default_list[index]
                    arg_map[handle_arg] = handle_default_list[index]
        return arg_map


def load_alarm_task_cls():
    """load all alarm task, include cls name"""
    alarm_list = []
    con_list = list()
    task_dir = os.path.dirname(os.path.realpath(__file__))
    alarm_module_dir = os.path.dirname(task_dir)
    logger.info("[load_alarm_task] alarm_dir={}, task_dir={}".format(alarm_module_dir, task_dir))
    if alarm_module_dir not in sys.path:
        sys.path.append(alarm_module_dir)
    mods = [mod for _, mod, _ in pkgutil.iter_modules([task_dir])]
    logger.info("[load_alarm_task] mods={}".format(mods))
    for mod_name in mods:
        mod = importlib.import_module('.alarm_module.task.{}'.format(mod_name), package='open_infra.apps.alarm.resources')
        for _, cls in list(mod.__dict__.items()):
            if inspect.isclass(cls):
                try:
                    if list(cls.__base__.__dict__.keys()) == list(BaseAlarm.__dict__.keys()):
                        if cls.__name__ not in con_list:
                            con_list.append(cls.__name__)
                            alarm_list.append(cls)
                except Exception as e:
                    logger.error("[load_alarm_task] {}".format(e))
    return alarm_list


def get_all_alarm_fun():
    """获取所有注册的告警方法"""
    resource_cls_list = load_alarm_task_cls()
    endpoint_list = []
    for resource_cls in resource_cls_list:
        resource_obj = resource_cls()
        for endpoint in resource_obj.endpoints():
            func_obj = getattr(resource_obj, endpoint.__name__)
            endpoint_list.append(func_obj)
    return endpoint_list


# print get_all_alarm_fun()
if __name__ == '__main__':
    print(get_all_alarm_fun())
