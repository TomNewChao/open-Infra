# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 9:27
# @Author  : Tom_zc
# @FileName: constants.py
# @Software: PyCharm
from threading import Lock


class GitHubPrStatus(object):
    """the status of webhook"""
    create = "created"
    opened = "opened"
    reopened = "reopened"
    closed = "closed"

    @classmethod
    def is_in_github_pr_status(cls, status):
        if status in [cls.create, cls.opened, cls.reopened, cls.closed]:
            return True
        else:
            return False

    @classmethod
    def is_in_new_pr_status(cls, status):
        if status in [cls.opened, cls.reopened]:
            return True
        else:
            return False


class KubeConfigRole:
    """the Role of kubeconfig"""
    admin = "admin"
    developer = "developer"
    viewer = "viewer"

    @classmethod
    def is_in_kubeconfig_role(cls, role):
        if role in [cls.admin, cls.developer, cls.viewer]:
            return True
        else:
            return False


class KubeConfigLock:
    """The lock of kubeconfig"""
    ProcessLock = Lock()


class PermissionGlobalConfig:
    """The permission of global config"""
    comment_github_url = "{}/repos/{}/{}/issues/{}/comments"
    merge_github_url = "{}/repos/{}/{}/pulls/{}/merge"
    service_txt_url = "https://api.github.com/repos/Open-Infra-Ops/kubeconfig-community/contents/doc/ServiceName.txt"


class PrComment:
    """The permission of comment"""
    welcome = """Hi ***{}***, welcome to the Open-Infra-Ops Community.\nI'm the Bot here serving you.Thank you for submitting the kubeconfig request.\nApplication check result: ***{}***.\nDetail: {}"""
    error = "The internal service is abnormal, Please contact the warehouse administrator."
