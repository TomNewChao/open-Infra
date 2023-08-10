# -*- coding: utf-8 -*-

import logging
import time
import hashlib
import datetime
import threading
import traceback

from alarm.models import Alarm
from alarm.resources.alarm_module.alarm_server import AlarmServer
from alarm.resources.alarm_module.common import calc_next_run_time
from alarm.resources.alarm_module.task import get_all_alarm_fun
from open_infra.utils.common import unicode_convert

logger = logging.getLogger("alarm")


class AlarmGlobalConfig:
    # task list
    TASK_LIST = []
    TASK_LIST_LOCK = threading.Lock()

    # refresh alarm status
    EXPIRES = 5 * 60  # alarm status time
    LOCK = threading.Lock()  # exec_alarm

    ALARM_STATUS_DICT = {}  # {"md5sum": {" status": 0 ok/alarm 1, "expires": GlobalConfig.EXPIRES, "time": time.time()}
    RETRY_NEED_TASK_DICT = {}  # {"md5sum": 0}

    # global config
    REAL_EXECUTION = False  # first to collect task
    MAX_RUNNING_TIME = 1 * 60  # max running time


class AlarmTools(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self.server = AlarmServer()

    @staticmethod
    def get_alarm_md5(alarm_name, alarm_md5_list):
        """获取未恢复的报警"""
        alarm_list = Alarm.objects.filter(alarm_name=alarm_name).filter(is_recover=False).values("alarm_md5")
        exist_alarm_list = [alarm_dict["alarm_md5"] for alarm_dict in alarm_list]
        return list(set(exist_alarm_list) - set(alarm_md5_list))

    @staticmethod
    def get_run_min_interval(min_run_time):
        """获取最小的运行时间和当前时间的时间间隔"""
        min_run_timedelta = min_run_time - datetime.datetime.now()
        if min_run_timedelta.days < 0:
            return False, None
        else:
            return True, min_run_timedelta.total_seconds()

    @staticmethod
    def update_func(alarm_task_list):
        """将函数对象修改为绑定函数对象"""
        for bind_alarm_task in alarm_task_list:
            func = bind_alarm_task.__func__
            func_self = bind_alarm_task.__self__
            func_name = func.__name__
            for task in AlarmGlobalConfig.TASK_LIST:
                task_func = task['func_obj']
                task_func_name = task_func.__name__
                try:
                    args = task['args']
                    task_func_self = args[0]
                    if func_name == task_func_name and func_self == task_func_self:
                        task['func_obj'] = bind_alarm_task
                except Exception as e:
                    logger.error(e.args[0])

    @staticmethod
    def handle_alarm_task():
        """执行任务队列中，运行时间小于或等于当前时间的任务"""
        now_time = datetime.datetime.now()
        for task_dict in AlarmGlobalConfig.TASK_LIST:
            run_time = task_dict['run_time']
            if now_time >= run_time and not task_dict['run_status']:
                func_obj = task_dict['func_obj']
                # logger.info('[handle_alarm_task] func_name:{}'.format(func_obj.__func__.__name__))
                args = task_dict['args']
                if args:
                    args = args[1:]
                kwargs = task_dict['kwargs']
                func_obj(*args, **kwargs)

    @classmethod
    def get_alarm_str_by_conf(cls, var_dict):
        """通过字符串生成md5"""
        var_dict = unicode_convert(var_dict)
        alarm_id = var_dict.get('alarm_id')
        alarm_arg_list = var_dict.get('des_var')
        alarm_str = '{}_{}'.format(alarm_id, alarm_arg_list)
        return alarm_str

    @classmethod
    def gen_alarm_md5(cls, var_dict):
        """生成报警的md5字符串"""
        alarm_str = cls.get_alarm_str_by_conf(var_dict)
        md5_obj = hashlib.md5()
        md5_obj.update(alarm_str.encode('utf-8'))
        return md5_obj.hexdigest()

    @staticmethod
    def _check_expires(alarm_status_dict):
        """检测告警状态超时时间，如果超时，则返回True，否则返回False"""
        if alarm_status_dict is not None:
            time_val = alarm_status_dict['time']
            expires = alarm_status_dict['expires']
            time_interval = time.time() - time_val
            if time_interval > expires:
                return True
        return False

    def exc_alarm(self, alarm_dict):
        """
        执行报警
        @param alarm_dict:{
                        "alarm_type": 报警类型, 0: 恢复， 1:报警
                        "alarm_info_dict": 报警内容
                          {
                            "alarm_id":
                            "des_var":
                          }
                        "report_retry_count": 重试次数
                        }
        @return:
        """
        alarm_type = alarm_dict.get('alarm_type')
        alarm_info_dict = alarm_dict.get('alarm_info_dict')
        report_retry_count = alarm_dict.get('report_retry_count')
        md5_str = self.gen_alarm_md5(alarm_info_dict)
        alarm_info_dict['md5'] = md5_str
        with AlarmGlobalConfig.LOCK:
            logger.debug("[exc_alarm] md5:{}".format(md5_str))
            alarm_status_dict = AlarmGlobalConfig.ALARM_STATUS_DICT.get(md5_str)
            # 上报告警
            logger.debug("[exc_alarm] alarm_status_val:{}".format(alarm_status_dict))
            if self._check_expires(alarm_status_dict):
                alarm_status_dict = None
            # 0 recovery/1 alarm
            if alarm_type:
                # check status expires or last time is ok
                if alarm_status_dict is None or alarm_status_dict['status'] == 0:
                    if report_retry_count:
                        retry_count = AlarmGlobalConfig.RETRY_NEED_TASK_DICT.get(md5_str)
                        retry_count = retry_count if retry_count is not None else 0
                        if retry_count < (report_retry_count - 1):
                            retry_count += 1
                            AlarmGlobalConfig.RETRY_NEED_TASK_DICT[md5_str] = retry_count
                            return True
                        else:
                            AlarmGlobalConfig.RETRY_NEED_TASK_DICT[md5_str] = 0
                    is_send_ok = self.server.send(alarm_info_dict)
                    if not is_send_ok:
                        return False
                    AlarmGlobalConfig.ALARM_STATUS_DICT[md5_str] = {
                        "status": 1,
                        "expires": AlarmGlobalConfig.EXPIRES,
                        "time": time.time()
                    }
                    return True
                else:
                    logger.debug('[exc_alarm] report alarm intercept........................')
                    return True
            else:
                if md5_str in AlarmGlobalConfig.RETRY_NEED_TASK_DICT:
                    AlarmGlobalConfig.RETRY_NEED_TASK_DICT[md5_str] = 0
                # if expire
                if alarm_status_dict is None:
                    is_send_ok = self.server.send({'md5': md5_str})
                    if not is_send_ok:
                        return False
                    AlarmGlobalConfig.ALARM_STATUS_DICT[md5_str] = {
                        "status": 0,
                        "expires": AlarmGlobalConfig.EXPIRES,
                        "time": time.time()
                    }
                    return True
                # if ok
                elif alarm_status_dict['status'] == 0:
                    logger.debug('[exc_alarm] recover alarm intercept........................')
                    return True
                # if alarm
                elif alarm_status_dict['status'] == 1:
                    is_send_ok = self.server.send({'md5': md5_str})
                    if not is_send_ok:
                        return False
                    AlarmGlobalConfig.ALARM_STATUS_DICT[md5_str] = {
                        "status": 0,
                        "expires": AlarmGlobalConfig.EXPIRES,
                        "time": time.time()
                    }
                    return True
        return True

    # noinspection PyMethodMayBeStatic
    def recover_alarm(self, alarm_md5_list):
        for alarm_md5_str in alarm_md5_list:
            self.server.recover_alarm(alarm_md5_str)
            if alarm_md5_str in AlarmGlobalConfig.ALARM_STATUS_DICT.keys():
                del AlarmGlobalConfig.ALARM_STATUS_DICT[alarm_md5_str]
            if alarm_md5_str in AlarmGlobalConfig.RETRY_NEED_TASK_DICT.keys():
                del AlarmGlobalConfig.RETRY_NEED_TASK_DICT[alarm_md5_str]

    def exec_alarm_obj(self, alarm_obj):
        """根据参数判断告警类型，在内存中添加告警状态，告警状态判断通过的，将消息传入队列中"""
        if isinstance(alarm_obj, dict):
            self.exc_alarm(alarm_obj)
        elif isinstance(alarm_obj, list):
            for alarm_dict in alarm_obj:
                self.exc_alarm(alarm_dict)


def active_alarm(alarm_dict):
    """主动上报告警函数
    :param  alarm_dict:
    {
    "alarm_type": 报警类型, 0: 恢复， 1:报警
    "report_retry_count": 重试次数
    "alarm_info_dict": 报警内容
          {
            "alarm_id":
            "des_var":
          }
    }
    :return:
    """
    try:
        base_obj = AlarmTools()
        logger.debug("[active_alarm]:{}".format(alarm_dict))
        base_obj.exec_alarm_obj(alarm_dict)
    except Exception as e:
        logger.error("[active_alarm] fail:{}, traceback:{}".format(e, traceback.format_exc()))
        return False
    return True


def batch_recover_alarm(alarm_md5_list):
    """批量手动消除报警
    @param alarm_md5_list: ["md5_list"]
    @return:
    """
    try:
        if not alarm_md5_list:
            return True
        base_obj = AlarmTools()
        base_obj.recover_alarm(alarm_md5_list)
    except Exception as e:
        logger.error("[batch_recover_alarm] fail:{}".format(e))
        return False
    return True


def batch_recover_faded_alarm(alarm_name, alarm_md5_list):
    """针对于在报警中里面消逝的报警，进行手动恢复
    @param alarm_name: 报警名称
    @param alarm_md5_list: 报警md5列表
    @return:
    """
    try:
        base_obj = AlarmTools()
        alarm_md5_list = base_obj.get_alarm_md5(alarm_name, alarm_md5_list)
        batch_recover_alarm(alarm_md5_list)
    except Exception as e:
        logger.error("[batch_recover_faded_alarm] fail:{}".format(e))
        return False
    return True


class Task(object):
    def __init__(self, exec_interval, wait_for, is_active, real_arg_dict, fn, args, kwargs, executor,
                 exception_handler=None):
        super(Task, self).__init__()
        self.wait_for = wait_for
        self.exec_interval = exec_interval
        self.fn = fn
        self.is_active = is_active
        self.fn_args = args
        self.real_arg_dict = real_arg_dict
        self.fn_kwargs = kwargs
        self.executor = executor
        self.ex_handler = exception_handler
        self.running = False
        self.event = threading.Event()
        self.progress = None
        self.ret_value = None
        self.begin_time = None
        self.end_time = None
        self.duration = 0
        self.exception = None
        self.lock = threading.Lock()

    def task_run(self):
        with self.lock:
            self.executor.task = self
            self.begin_time = time.time()
        self.executor.start()

    def complete(self, ret_value, exception=None):
        now = time.time()
        with self.lock:
            self.exception = exception
            self.duration = now - self.begin_time
        if self.is_active or not ret_value:
            logger.debug("[Task] complete: task is activate or ret_value is empty")
            return
        if self.duration <= self.wait_for:
            AlarmTools().exec_alarm_obj(ret_value)
        else:
            logger.info("{} timeout".format(self.fn))
            AlarmTools().exec_alarm_obj(ret_value)
        logger.debug("[Task]: execution of %s finished in: %s s", self, self.duration)


class ThreadedExecutor(object):
    def __init__(self, wait_for):
        self.task = None
        self.wait_for = wait_for
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True

    def start(self):
        logger.debug('[ThreadedExecutor] task start.'.format(self.task.fn))
        task_name = self.task.fn.__name__
        # look for the alarm func according the func name and args and set status to True, and start thread
        with AlarmGlobalConfig.TASK_LIST_LOCK:
            for task_dict in AlarmGlobalConfig.TASK_LIST:
                bind_func_name = task_dict['func_obj'].__func__.__name__
                if task_name == bind_func_name:
                    args = task_dict['args']
                    if args == self.task.fn_args:
                        task_dict['run_status'] = True
        self._thread.start()

    def _run(self):
        """finish task and set status to False"""
        try:
            ret_value = self.task.fn(*self.task.fn_args, **self.task.fn_kwargs)
            exception = None
        except Exception as e:
            logger.error('[ThreadedExecutor] _run:{}'.format(e))
            ret_value = None
            exception = e
        logger.debug('[ThreadedExecutor] _run:{}'.format(ret_value))
        task_name = self.task.fn.__name__
        with AlarmGlobalConfig.TASK_LIST_LOCK:
            for task_dict in AlarmGlobalConfig.TASK_LIST:
                bind_func_name = task_dict['func_obj'].__func__.__name__
                if task_name == bind_func_name:
                    args = task_dict['args']
                    if args == self.task.fn_args:
                        exec_interval = task_dict['exec_interval']
                        next_run_time = calc_next_run_time(exec_interval)
                        logger.debug('[ThreadedExecutor] {} next run time {}'.format(self.task.fn, next_run_time))
                        task_dict['run_time'] = next_run_time
                        task_dict['run_status'] = False
        logger.debug("[ThreadedExecutor] _run: {} task run time and status modified successfully".format(self.task.fn))
        self.task.complete(ret_value, exception)


class TaskManager(object):
    @classmethod
    def run(cls, exec_interval, wait_for, is_active, real_arg_dict, fn, args=None, kwargs=None, executor=None,
            exception_handler=None):
        if not args:
            args = []
        if not kwargs:
            kwargs = {}
        if not executor:
            executor = ThreadedExecutor(wait_for)
        logger.debug('[TaskManager]: {} end of thread assignment'.format(fn))
        task = Task(exec_interval, wait_for, is_active, real_arg_dict, fn, args, kwargs, executor, exception_handler)
        logger.debug("[TaskManager]: running %s", task)
        task.task_run()
        return task


class AlarmClient(threading.Thread):

    def __init__(self):
        super(AlarmClient, self).__init__()
        self.self_stop = False
        self.daemon = True

    def work_thread(self):
        logger.info("[AlarmClient] start to work...")
        try:
            # 1.collect func
            base_obj = AlarmTools()
            alarm_task_list = get_all_alarm_fun()
            for alarm_task in alarm_task_list:
                try:
                    alarm_task()
                except Exception as e:
                    logger.error("[AlarmClient] {} exc fail".format(alarm_task))
                    logger.exception(e)
            # 2.start to really execute
            AlarmGlobalConfig.REAL_EXECUTION = True
            base_obj.update_func(alarm_task_list)
            logger.info("[AlarmClient] collect task list:{}".format(AlarmGlobalConfig.TASK_LIST))
            while not self.self_stop:
                with AlarmGlobalConfig.TASK_LIST_LOCK:
                    # if task_list is empty, return
                    if not AlarmGlobalConfig.TASK_LIST:
                        logger.warning("[AlarmClient] no tasks are current registered")
                        return
                    # get first task, if running, set min_run_time is max
                    min_next_run_time = AlarmGlobalConfig.TASK_LIST[0]['run_time']
                    status = AlarmGlobalConfig.TASK_LIST[0]['run_status']
                    if status:
                        min_next_run_time = datetime.datetime.max
                    copy_task_list = AlarmGlobalConfig.TASK_LIST[1:]
                    for task_dict in copy_task_list:
                        if task_dict['run_status']:
                            logger.debug("[AlarmClient] current task in progress, skipping")
                            continue
                        run_time = task_dict['run_time']
                        if run_time < min_next_run_time:
                            status = False
                            min_next_run_time = run_time
                if status:
                    # logger.warning("[AlarmClient] tasks are all in progress，try again")
                    time.sleep(1)
                    continue
                min_run_time_interval_ret = base_obj.get_run_min_interval(min_next_run_time)
                if not min_run_time_interval_ret[0]:
                    logger.debug('[AlarmClient] the current time is greater than the minimum run time.'
                                 'do not wait，execute directly')
                    base_obj.handle_alarm_task()
                elif min_run_time_interval_ret[1]:
                    min_run_time_interval = min_run_time_interval_ret[1]
                    if AlarmGlobalConfig.MAX_RUNNING_TIME < min_run_time_interval:
                        logger.warning('[AlarmClient] max wait:{} second'.format(min_run_time_interval))
                        min_run_time_interval = AlarmGlobalConfig.MAX_RUNNING_TIME
                    # logger.info('[AlarmClient] wait:{} second'.format(min_run_time_interval))
                    time.sleep(min_run_time_interval)
                    base_obj.handle_alarm_task()
                else:
                    logger.info('[AlarmClient] the time is more than 0 second and less than 1 second, '
                                'wait for 0.5 seconds to execute')
                    time.sleep(0.5)
        except Exception as e:
            logger.error("[AlarmClient] work thread fail:{}, traceback:{}".format(e, traceback.format_exc()))

    def run(self):
        logger.info('[AlarmClient] Start alarm routine thread.')
        self.work_thread()
        logger.info('[AlarmClient] Quit alarm routine thread.')

    def stop(self):
        logger.info("[AlarmClient] Stopping alarm routine thread.")
        self.self_stop = True
        logger.info("[AlarmClient] Stopped alarm routine thread.")


if __name__ == '__main__':
    alarm_client = AlarmClient()
    alarm_client.start()
