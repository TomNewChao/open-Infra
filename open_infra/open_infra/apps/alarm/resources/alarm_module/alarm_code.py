# -*-coding:utf-8 -*-
import traceback
import logging
from django.conf import settings

from open_infra.utils.common import unicode_convert

logger = logging.getLogger("django")


class AlarmCodeConfig:
    is_cn = settings.LANGUAGE_CODE.lower() == "zh-hans"


class AlarmLevel:
    """The definition of Alarm level."""
    CRITICAL = 0
    MAJOR = 1  # le 1 and send mail
    MINOR = 2
    WARNING = 3
    NOTE = 4

    ALARM_LEVEL_COLOR = {
        CRITICAL: '#ff0000',
        MAJOR: '#F56C6C',
        MINOR: '#a26300',
        WARNING: '#e6a23c',
        NOTE: '#67c23a'
    }

    CN_ALARM_LEVEL = {
        CRITICAL: '严重',
        MAJOR: '重要',
        MINOR: '次要',
        WARNING: '警告',
        NOTE: '提示'
    }

    EN_ALARM_LEVEL = {
        CRITICAL: 'CRITICAL',
        MAJOR: 'MAJOR',
        MINOR: 'MINOR',
        WARNING: 'WARNING',
        NOTE: 'NOTE'
    }


class AlarmModule:
    """The definition of sub-modules which may generate alarm info."""
    MODULE_MONITOR = 0

    CN_ALARM_MODULE = {
        MODULE_MONITOR: "性能监控",
    }

    EN_ALARM_MODULE = {
        MODULE_MONITOR: "monitor",
    }

    @classmethod
    def get_module_desc_by_id(cls, module_id):
        if AlarmCodeConfig.is_cn:
            return AlarmModule.CN_ALARM_MODULE.get(module_id)
        else:
            return AlarmModule.EN_ALARM_MODULE.get(module_id)


class AlarmCode:
    # MONITOR ALARM CODE
    MONITOR_DESC_CODE_BASE = 0
    MONITOR_DESC_CODE_NODE_CPU_OVERFLOW = MONITOR_DESC_CODE_BASE + 1
    MONITOR_DESC_CODE_NODE_MEM_OVERFLOW = MONITOR_DESC_CODE_BASE + 2
    MONITOR_DESC_CODE_NODE_DISK_OVERFLOW = MONITOR_DESC_CODE_BASE + 2

    MONITOR_DESC_CODE_CONTAINER_CPU_OVERFLOW = MONITOR_DESC_CODE_BASE + 2
    MONITOR_DESC_CODE_CONTAINER_MEM_OVERFLOW = MONITOR_DESC_CODE_BASE + 2
    MONITOR_DESC_CODE_CONTAINER_DISK_OVERFLOW = MONITOR_DESC_CODE_BASE + 2

    CN_DESC_ALARM = {
        # MONITOR
        MONITOR_DESC_CODE_NODE_CPU_OVERFLOW: {
            'ALARM_NAME': '服务器CPU告警',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "服务器%s的CPU占用率超过%s。"
        },
        MONITOR_DESC_CODE_NODE_MEM_OVERFLOW: {
            'ALARM_NAME': '服务器内存告警',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "服务器%s内存使用率超过%s。"
        },
        MONITOR_DESC_CODE_NODE_DISK_OVERFLOW: {
            'ALARM_NAME': '系统盘使用率过高',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "服务器%s的系统盘已用空间超过%s。"
        },
        MONITOR_DESC_CODE_CONTAINER_CPU_OVERFLOW: {
            'ALARM_NAME': '容器CPU告警',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "服务器%s的CPU占用率超过%s。"
        },
        MONITOR_DESC_CODE_CONTAINER_MEM_OVERFLOW: {
            'ALARM_NAME': '容器内存告警',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "服务器%s内存使用率超过%s。"
        },
        MONITOR_DESC_CODE_CONTAINER_DISK_OVERFLOW: {
            'ALARM_NAME': '容器挂载盘使用率过高',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "服务器%s的系统盘已用空间超过%s。"
        }

    }

    EN_DESC_ALARM = {
        # MONITOR
        MONITOR_DESC_CODE_NODE_CPU_OVERFLOW: {
            'ALARM_NAME': 'server CPU alarm',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "server %s CPU is over %s。"
        },
        MONITOR_DESC_CODE_NODE_MEM_OVERFLOW: {
            'ALARM_NAME': 'server Memory alarm',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "server %s memory is over %s。"
        },
        MONITOR_DESC_CODE_NODE_DISK_OVERFLOW: {
            'ALARM_NAME': 'server disk alarm',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "server %s disk is over %s。"
        },
        MONITOR_DESC_CODE_CONTAINER_CPU_OVERFLOW: {
            'ALARM_NAME': 'container CPU alarm',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "container %s is over %s。"
        },
        MONITOR_DESC_CODE_CONTAINER_MEM_OVERFLOW: {
            'ALARM_NAME': 'container Memory alarm',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "container %s is over %s。"
        },
        MONITOR_DESC_CODE_CONTAINER_DISK_OVERFLOW: {
            'ALARM_NAME': 'container disk alarm',
            'ALARM_LEVEL': AlarmLevel.MAJOR,
            'ALARM_MODULE': AlarmModule.MODULE_MONITOR,
            'ALARM_CONTENT': "container %s is over %s。"
        }
    }

    @classmethod
    def trans_to_des_by_str(cls, alarm_id, des_var=None):
        if not des_var:
            des_var = []
        if AlarmCodeConfig.is_cn:
            cn_des = cls.CN_DESC_ALARM.get(alarm_id)
        else:
            cn_des = cls.EN_DESC_ALARM.get(alarm_id)
        alarm_des = dict()
        if cn_des is None:
            logger.info("[trans_to_des_by_str] Description code is invalid:{}".format(alarm_id))
            return None
        try:
            des = cn_des.get('ALARM_CONTENT')
            if isinstance(des, bytes):
                alarm_des['ALARM_CONTENT'] = des.decode('utf-8')
            else:
                alarm_des['ALARM_CONTENT'] = des
            if len(des_var) > 0:
                des_var = unicode_convert(des_var)
                alarm_des['ALARM_CONTENT'] = alarm_des['ALARM_CONTENT'] % tuple(des_var)
            alarm_des['ALARM_MODULE'] = cn_des.get('ALARM_MODULE')
            alarm_des['ALARM_LEVEL'] = cn_des.get('ALARM_LEVEL')
            alarm_des['ALARM_NAME'] = cn_des.get('ALARM_NAME')
            return alarm_des
        except Exception as e:
            logger.error("[trans_to_des_by_str] Exception: {},{}".format(e.args[0], traceback.format_exc()))
            return None
