# -*- coding: utf-8 -*-
# @Time    : 2022/7/7 10:30
# @Author  : Tom_zc
# @FileName: api_error_code.py
# @Software: PyCharm

from django.conf import settings
from logging import getLogger

logger = getLogger("django")


class ErrCode(object):
    STATUS_SUCCESS = 0  # successfully
    STATUS_PARAMETER_ERROR = -1
    STATUS_PARTIAL_SUCCESS = -2
    STATUS_RESULT_WARNING = -3
    INTERNAL_ERROR = -4
    SYSTEM_BUSY = -5
    NAME_NOT_STANDARD = -6
    RESULT_IS_EMPTY = -7
    STATUS_PARAMETER_CORRESPONDING_ERROR = -8

    STATUS_FAILED = 100000

    STATUS_SEREVITY_BIT_MASK = 30
    STATUS_SEREVITY_SUCCESS = 0b00 << STATUS_SEREVITY_BIT_MASK
    STATUS_SEREVITY_INFO = 0b01 << STATUS_SEREVITY_BIT_MASK
    STATUS_SEREVITY_WARN = 0b10 << STATUS_SEREVITY_BIT_MASK
    STATUS_SEREVITY_ERROR = 0b11 << STATUS_SEREVITY_BIT_MASK

    # facility code-----12 bit
    STATUS_FACILITY_BIT_MASK = 16
    STATUS_FACILITY_DASHBOARD = 1 << STATUS_FACILITY_BIT_MASK

    # err code zone
    # +---------------------------------------------------+
    # | sub module name       |          code zone        |
    # +---------------------------------------------------+
    # |      common           |          1~100            |
    # +---------------------------------------------------+
    # |      users            |          101~200          |
    # +---------------------------------------------------+
    # |      app_tools     |          201~300          |
    # +---------------------------------------------------+

    # sub module: common
    STATUS_COMMON_BASE = STATUS_FACILITY_DASHBOARD + 0
    STATUS_COMMON_START_SERVICE_FAILED = STATUS_SEREVITY_ERROR + STATUS_COMMON_BASE + 1

    # sub module: users
    STATUS_USERS_BASE = STATUS_FACILITY_DASHBOARD + 100
    STATUS_USER_LOGIN_FAIL = STATUS_SEREVITY_ERROR + STATUS_USERS_BASE + 1
    STATUS_USER_DISABLED_FAIL = STATUS_SEREVITY_ERROR + STATUS_USERS_BASE + 2

    # sub module: app_tools
    STATUS_CLOUDS_TOOLS_BASE = STATUS_FACILITY_DASHBOARD + 200
    STATUS_SCAN_ING = STATUS_SEREVITY_ERROR + STATUS_CLOUDS_TOOLS_BASE + 1
    STATUS_SCAN_FAILED = STATUS_SEREVITY_ERROR + STATUS_CLOUDS_TOOLS_BASE + 2
    STATUS_SCAN_CLEAN = STATUS_SEREVITY_ERROR + STATUS_CLOUDS_TOOLS_BASE + 3
    STATUS_PORT_EXIST = STATUS_SEREVITY_ERROR + STATUS_CLOUDS_TOOLS_BASE + 4

    # sub module: alarm_email
    STATUS_CLOUDS_ALARM = STATUS_FACILITY_DASHBOARD + 300
    STATUS_ALARM_EMAIL_NOT_EXIST = STATUS_SEREVITY_ERROR + STATUS_CLOUDS_ALARM + 1
    STATUS_ALARM_EMAIL_IS_EXIST = STATUS_SEREVITY_ERROR + STATUS_CLOUDS_ALARM + 2
    STATUS_ALARM_PHONE_NUMBER_IS_EXIST = STATUS_SEREVITY_ERROR + STATUS_CLOUDS_ALARM + 3

    # sub module: permission
    STATUS_CLOUDS_PERMISSION = STATUS_FACILITY_DASHBOARD + 400
    STATUS_KUBECONFIG_DELETE_FAILED = STATUS_CLOUDS_PERMISSION + 1

    _en_err_desc = {
        STATUS_SUCCESS: "Successfully",
        STATUS_PARTIAL_SUCCESS: "Partially successful, data may be incomplete, please check the cluster for exceptions",
        STATUS_PARAMETER_ERROR: "Parameter invalid.",
        STATUS_FAILED: "Failed.",
        INTERNAL_ERROR: 'internal error',
        SYSTEM_BUSY: 'The system is busy.',
        NAME_NOT_STANDARD: 'name not standard.',
        RESULT_IS_EMPTY: 'The result is empty.',
        STATUS_PARAMETER_CORRESPONDING_ERROR: 'Parameter corresponding invalid.',

        # for common
        STATUS_COMMON_START_SERVICE_FAILED: "Start (%s) service (%s) failed.",

        # for auth
        STATUS_USER_LOGIN_FAIL: "Auth failed.",
        STATUS_USER_DISABLED_FAIL: "Username has been disabled, please contact the administrator.",

        # for app_tools
        STATUS_SCAN_ING: "Scanning, Please wait.",
        STATUS_SCAN_FAILED: "No result, please try again.",
        STATUS_SCAN_CLEAN: "The background is trying again later, Please wait.",
        STATUS_PORT_EXIST: "The port is exist, Operation failed.",

        # for alarm
        STATUS_ALARM_EMAIL_NOT_EXIST: "The email is not exist, Operation failed.",
        STATUS_ALARM_EMAIL_IS_EXIST: "The email is exist, Operation failed.",
        STATUS_ALARM_PHONE_NUMBER_IS_EXIST: "The Phone number is exist, Operation failed.",

        # for permission
        STATUS_KUBECONFIG_DELETE_FAILED: "Partial deletion failed, list of failures: %s.",

    }

    _cn_err_desc = {
        # reserved error codes which will be handled specifically by front-end
        STATUS_SUCCESS: "操作成功。",
        STATUS_PARTIAL_SUCCESS: "部分成功，数据可能不完整，请检查集群是否存在异常。",
        STATUS_PARAMETER_ERROR: "参数错误。",
        STATUS_FAILED: "操作失败。",
        INTERNAL_ERROR: '系统内部错误，请稍后重试。',
        SYSTEM_BUSY: "系统繁忙，请稍后重试。",
        NAME_NOT_STANDARD: "名称不规范。",
        RESULT_IS_EMPTY: "没有满足条件的数据。",
        STATUS_PARAMETER_CORRESPONDING_ERROR: "存在参数对应关系错误。",

        # for common
        STATUS_COMMON_START_SERVICE_FAILED: "启动主机 (%s) 的服务 (%s) 失败。",

        # for auth
        STATUS_USER_LOGIN_FAIL: "用户名或者密码错误，登录失败。",
        STATUS_USER_DISABLED_FAIL: "用户已被禁用，请联系管理员。",


        # for app_tools
        STATUS_SCAN_ING: "正在扫描，请稍等。",
        STATUS_SCAN_FAILED: "查无结果，请重试。",
        STATUS_SCAN_CLEAN: "后台正在清理，请稍后重试。",
        STATUS_PORT_EXIST: "高危端口已存在，操作失败。",

        # for alarm
        STATUS_ALARM_EMAIL_NOT_EXIST: "报警通知策略不存在，操作失败。",
        STATUS_ALARM_EMAIL_IS_EXIST: "邮件已存在，操作失败。",
        STATUS_ALARM_PHONE_NUMBER_IS_EXIST: "手机号已存在，操作失败。",

        # for permission
        STATUS_KUBECONFIG_DELETE_FAILED: "删除失败，部分失败名单：%s。",

    }

    @classmethod
    def _get_en_err(cls, err_code):
        if err_code not in list(cls._en_err_desc.keys()):
            logger.error("The err code: %s not exists in en_error_desc.", err_code)
            return None
        return cls._en_err_desc[err_code]

    @classmethod
    def _get_cn_err(cls, err_code):
        if err_code not in list(cls._cn_err_desc.keys()):
            logger.error("The err code: %s not exists in cn_error_desc.", err_code)
            return None
        return cls._cn_err_desc[err_code]

    @classmethod
    def get_err_desc(cls, err_code, lang_flag=None):
        if lang_flag is None:
            lang_flag = settings.LANGUAGE_CODE
        if lang_flag == "zh-hans":
            return cls._get_cn_err(err_code)
        elif lang_flag == "en":
            return cls._get_en_err(err_code)
        else:
            logger.error("err_code need to adapter")
            return cls._get_en_err(err_code)
