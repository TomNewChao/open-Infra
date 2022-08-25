# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 11:27
# @Author  : Tom_zc
# @FileName: scan_thread.py
# @Software: PyCharm
from threading import Lock


class BaseStatus:

    @classmethod
    def get_status_comment(cls):
        dict_data = dict()
        for attr, content in cls.__dict__.items():
            if attr.isupper() and isinstance(content, tuple):
                dict_data[content[0]] = content[1]
        return dict_data

    @classmethod
    def get_comment_status(cls):
        dict_data = dict()
        for attr, content in cls.__dict__.items():
            if attr.isupper() and isinstance(content, tuple):
                dict_data[content[1]] = content[0]
        return dict_data


class HWCloudEipStatus(BaseStatus):
    FREEZED = (0, "冻结")
    BIND_ERROR = (1, "绑定失败")
    BINDING = (2, "绑定中")
    PENDING_CREATE = (3, "创建中")
    PENDING_DELETE = (4, "释放中")
    PENDING_UPDATE = (5, "更新中")
    NOTIFYING = (6, "通知绑定中")
    NOTIFY_DELETE = (7, "通知释放中")
    DOWN = (8, "未绑定")
    ACTIVE = (9, "绑定")
    ELB = (10, "绑定ELB")
    VPN = (11, "绑定VPN")
    ERROR = (12, "失败")


class HWCloudEipType(BaseStatus):
    EIP = (0, "全动态BGP")


class NetProtocol(object):
    TCP = 1
    UDP = 0


class BaseStatus(object):
    handler = 1
    finish = 2


class ScanPortStatus(BaseStatus):
    pass


class ScanObsStatus(BaseStatus):
    pass


class ScanToolsLock:
    scan_port = Lock()
    scan_obs = Lock()
