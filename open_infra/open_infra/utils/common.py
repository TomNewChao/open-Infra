# -*- coding: utf-8 -*-
# @Time    : 2022/7/7 10:30
# @Author  : Tom_zc
# @FileName: common.py
# @Software: PyCharm

import time
import base64
import pickle
import subprocess
import tempfile
import traceback

from functools import wraps
from collections import Mapping
from collections import Iterable
from itsdangerous.jws import TimedJSONWebSignatureSerializer
from django.conf import settings
from logging import getLogger

from .api_error_code import ErrCode

logger = getLogger(__file__)


def func_retry(tries=3, delay=1):
    def deco_retry(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            for i in range(tries):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    print(e)
                    time.sleep(delay)
            else:
                print("func_retry: {} failed".format(fn.__name__))

        return inner

    return deco_retry


def pick_dumps(json_dict):
    json_bytes = pickle.dumps(json_dict)
    json_secret = base64.b64encode(json_bytes)
    json_str = json_secret.decode()
    return json_str


def pick_loads(json_str):
    json_secret = json_str.encode()
    json_bytes = base64.b64decode(json_secret)
    json_dict = pickle.loads(json_bytes)
    return json_dict


# noinspection PyShadowingBuiltins
def bytes_convert_str(input):
    if isinstance(input, dict):
        return {bytes_convert_str(key): bytes_convert_str(value) for key, value in input.items()}
    elif isinstance(input, (list, tuple)):
        return [bytes_convert_str(element) for element in input]
    elif isinstance(input, bytes):
        return input.decode('utf-8')
    elif isinstance(input, str):
        return input
    elif isinstance(input, Iterable):
        return [bytes_convert_str(element) for element in input]
    else:
        return input


# noinspection PyShadowingBuiltins
def unicode_convert(input):
    if isinstance(input, Mapping):
        return {unicode_convert(key): unicode_convert(value) for key, value in input.items()}
    elif isinstance(input, (tuple, list)):
        return [unicode_convert(element) for element in input]
    elif isinstance(input, bytes):
        return input.decode('utf-8')
    else:
        return input


def dumps(json_dict, expires):
    """加密: 将字典加密成字节，再解码"""
    serial_alter = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=expires)
    json_str = serial_alter.dumps(json_dict).decode()
    return json_str


def loads(json_str, expires):
    """解密：将字符串解密成字典，"""
    serial_alter = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=expires)
    try:
        json_dict = serial_alter.loads(json_str)
    except Exception as e:
        logger.error("e:{}".format(e))
        return None
    else:
        return json_dict


def execute_cmd3(cmd, timeout=30, err_log=True):
    try:
        logger.debug("execute_cmd3 call cmd: %s" % cmd)
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, close_fds=True)
        t_wait_seconds = 0
        while True:
            if p.poll() is not None:
                break
            if timeout >= 0 and t_wait_seconds >= (timeout * 100):
                p.terminate()
                return -1, "", "execute_cmd3 exceeded time {0} seconds in executing: {1}".format(timeout, cmd)
            time.sleep(0.01)
            t_wait_seconds += 1
        out, err = p.communicate()
        out, err = bytes_convert_str(out), bytes_convert_str(err)
        ret = p.returncode

        if ret != 0 and err_log:
            logger.error("execute_cmd3 cmd %s return %s, std output: %s, err output: %s.", cmd, ret, out, err)

        return ret, out, err
    except Exception as e:
        return -1, "", "execute_cmd3 exceeded raise, e={0}, trace={1}".format(e.args[0], traceback.format_exc())


def execute_cmd3_with_tmp(cmd_str, timeout=30):
    """
    针对输出结果超量的命令执行
    :param cmd_str 执行的命令
    :param timeout 超时时间
    :return:
    """
    try:
        with tempfile.NamedTemporaryFile() as out_tmp_file:
            # 1.写入内存临时文件
            cmd = cmd_str + ' > {}'.format(out_tmp_file.name)
            ret, out, err = execute_cmd3(cmd, timeout=timeout)
            if ret != 0:
                return ret, out, err
            # 2.读取到变量
            out_tmp_file.seek(0)  # 游标归0
            with open(out_tmp_file.name, 'r') as f:
                out_data = f.read()
            return ret, out_data, err
    except Exception as e:
        return -1, "", "execute_cmd3_with_tmp exceeded raise, e={0}, trace={1}".format(e.args[0],
                                                                                       traceback.format_exc())


class MgrException(Exception):
    def __init__(self, code, trans_para=None, trans_code=None, message=None, desc=None):
        self.code = code
        if isinstance(trans_para, str):
            trans_para = [trans_para]
        self.trans_para = trans_para
        self.trans_code = trans_code
        if desc is None:
            self.desc = translate_error_desc(code, [] if trans_para is None else trans_para)
        else:
            self.desc = desc
        super(MgrException, self).__init__(self.desc if message is None else message)


def auto_response():
    """
    Decorator that reports the execution time.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kw):
            # noinspection PyBroadException
            try:
                data = func(*args, **kw)
            except MgrException as e:
                logger.error(traceback.format_exc())
                return assemble_api_result(e.code, e.trans_code, e.trans_para)
            except Exception:
                logger.error(traceback.format_exc())
                return assemble_api_result(ErrCode.INTERNAL_ERROR)
            else:
                return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)

        return wrapper

    return decorator


# noinspection DuplicatedCode
def translate_error_desc(trans_code, trans_para=None):
    if trans_para is None:
        trans_para = list()
    tmp_desc = ErrCode.get_err_desc(trans_code)
    if tmp_desc is not None:
        try:
            tmp_desc = unicode_convert(tmp_desc)
            trans_desc = tmp_desc
            if len(trans_para) != 0:
                trans_para = unicode_convert(trans_para)
                trans_desc = tmp_desc % (tuple(trans_para))
        except Exception as e:
            logger.warning("Format error desc for %s failed: %s.", trans_code, str(e))
            trans_desc = tmp_desc
    else:
        if trans_code == 0:
            trans_desc = ErrCode.get_err_desc(trans_code)
        else:
            trans_desc = ErrCode.get_err_desc(ErrCode.STATUS_FAILED)

    return trans_desc


# noinspection DuplicatedCode
def assemble_api_result(err_code, trans_code=None, trans_para=None, data=None, lang_flag=None, replace_none=True):
    """
    : lang_flag: 指定返回结果描述的语言类型  cn/en
    """
    if trans_para is None:
        trans_para = []
    else:
        if isinstance(trans_para, str):
            trans_para = [trans_para]
    if replace_none and data is None:
        data = {}

    api_ret = {'err_code': err_code}
    if not trans_code:
        trans_code = err_code
    tmp_desc = ErrCode.get_err_desc(trans_code, lang_flag=lang_flag)
    if tmp_desc is not None:
        try:
            tmp_desc = unicode_convert(tmp_desc)
            trans_desc = tmp_desc
            if len(trans_para) != 0:
                trans_para = unicode_convert(trans_para)
                trans_desc = tmp_desc % (tuple(trans_para))
        except Exception as e:
            logger.warning("Format error desc for %s failed: %s.", trans_code, str(e))
            trans_desc = tmp_desc
        api_ret['description'] = trans_desc
    else:
        if err_code == 0:
            trans_desc = ErrCode.get_err_desc(err_code, lang_flag=lang_flag)
        else:
            trans_desc = ErrCode.get_err_desc(ErrCode.STATUS_FAILED, lang_flag=lang_flag)

        api_ret['description'] = trans_desc
    api_ret['data'] = data

    return api_ret
