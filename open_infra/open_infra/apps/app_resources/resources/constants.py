# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 11:27
# @Author  : Tom_zc
# @FileName: scan_thread.py
# @Software: PyCharm
from threading import Lock
from open_infra.utils.common import BaseStatus


class HWCloudEipStatus(BaseStatus):
    """Eip Status"""
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
    """Eip Type"""
    EIP = (0, "全动态BGP")
