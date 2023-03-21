# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 11:27
# @Author  : Tom_zc
# @FileName: scan_thread.py
# @Software: PyCharm
from threading import Lock
from open_infra.utils.common import BaseStatus


class NetProtocol(object):
    """Network  Protocol"""
    TCP = 1
    UDP = 0


class ScanBaseStatus(object):
    """the scan base status"""
    handler = 1
    finish = 2


class ScanPortStatus(ScanBaseStatus):
    pass


class ScanObsStatus(ScanBaseStatus):
    pass


class ScanToolsLock:
    """the all lock about app clouds tools"""
    scan_port = Lock()
    scan_obs = Lock()
    refresh_service_info_lock = Lock()
    obs_interact_lock = Lock()


