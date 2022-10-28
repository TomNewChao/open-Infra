# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 11:27
# @Author  : Tom_zc
# @FileName: scan_thread.py
# @Software: PyCharm
from threading import Lock

from open_infra.utils.common import BaseStatus


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


class ScanBaseStatus(object):
    handler = 1
    finish = 2


class ScanPortStatus(ScanBaseStatus):
    pass


class ScanObsStatus(ScanBaseStatus):
    pass


class ScanToolsLock:
    scan_port = Lock()
    scan_obs = Lock()


class ObsInteractComment(object):
    """The permission of comment"""
    error = "The internal service is abnormal, Please contact the warehouse administrator."
    welcome = """Hi ***{}***, welcome to the Open-Infra-Ops Community.\nI'm the Bot here serving you.Thank you for submitting the obs request.\nApplication check result: ***{}***.\nDetail: {}"""
    lgtm = """Hi, Thank you for your application. The information about your application has been sent to you by email, please check it carefully."""
    valid_lgtm = "Hi, lgtm should be confirmed by the repository administrator: {}."
    check_upload_ok = """Congratulations, the uploaded file passed the inspection successfully, this PR request will be closed automatically"""
    check_upload_false = """Unfortunately, the file you uploaded did not pass the inspection, and the reason for the failure to pass the inspection:{}"""


class Community(BaseStatus):
    Infrastructure = (0, "infrastructure")
    MindSpore = (1, "mindspore")
    openGauss = (2, "opengauss")
    openEuler = (3, "openeuler")
    openLooKeng = (4, "openlookeng")

    @classmethod
    def is_in_community(cls, community):
        if community in cls.get_comment_status():
            return True
        else:
            return False
