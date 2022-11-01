# -*- coding: utf-8 -*-
# @Time    : 2022/10/25 9:58
# @Author  : Tom_zc
# @FileName: utils_git.py
# @Software: PyCharm
import abc
import requests
import re
from logging import getLogger

logger = getLogger("django")


class GitHubPrStatus(object):
    """the status of webhook"""
    create = "created"
    opened = "opened"
    reopened = "reopened"
    closed = "closed"

    @classmethod
    def is_in_github_pr_status(cls, status):
        """judge github post status in this class"""
        if status in [cls.create, cls.opened, cls.reopened, cls.closed]:
            return True
        else:
            return False

    @classmethod
    def is_in_new_pr_status(cls, status):
        """judge github post action is new pr"""
        if status in [cls.opened, cls.reopened]:
            return True
        else:
            return False


class GitBase(metaclass=abc.ABCMeta):
    """the base class of git"""
    kubeconfig_interact_tools_lib = None
    comment_github_url = "{}/repos/{}/{}/issues/{}/comments"
    merge_github_url = "{}/repos/{}/{}/pulls/{}/merge"

    def __init__(self, pr_dict):
        self.pr_dict = pr_dict

    def create_pr(self):
        raise NotImplemented

    def comment_pr(self, comment):
        raise NotImplemented

    def merge_pr(self):
        raise NotImplemented


class GitBaseToolsLib(object):

    @classmethod
    def request_comment(cls, url, token, body_data, timeout=60):
        """request github api for comment"""
        header = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer {}".format(token)
        }
        result = requests.post(url, headers=header, json={"body": body_data}, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception(
                "[request_comment] request url:{} failed,code:{}, content:{}".format(url, result.content,
                                                                                     result.content))
        return result

    @classmethod
    def request_url(cls, url, timeout=60):
        """request github api for data"""
        result = requests.get(url, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception(
                "[request_diff] request url:{} failed,code:{}, content:{}".format(url, result.content, result.content))
        return result.content.decode("utf-8")

    @classmethod
    def request_merge(cls, url, token, timeout=60):
        """request github api for merge"""
        header = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer {}".format(token)
        }
        result = requests.put(url, headers=header, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception(
                "[request_merge] request url:{} failed,code:{}, content:{}".format(url, result.content, result.content))
        return result

    @classmethod
    def parse_diff(cls, parse_content):
        """Parse the data submitted by git and get it from the pr.diff file"""
        result_list = parse_content.split("+++ ")
        list_data = list()
        for result in result_list:
            dict_data = dict()
            for line in result.split("\n"):
                if line.startswith("+") and not line.startswith("++"):
                    list_line = line[1:].split(":")
                    if len(list_line) != 2:
                        continue
                    dict_data[list_line[0].strip().lower()] = list_line[1].strip()
            if len(dict_data):
                list_data.append(dict_data)
        logger.info("[GitBaseToolsLib] parse_diff parse data:{}".format(list_data))
        return list_data

    @classmethod
    def parse_patch(cls, parse_content):
        """Parse the data submitted by git and get it from the pr.pathch file"""
        result_list = parse_content.split("+++ ")
        email_str = str()
        for result in result_list:
            for line in result.split("\n"):
                if line.startswith("From:"):
                    email_temp = re.findall(r"<.*?>", line)
                    if len(email_temp):
                        email_str = email_temp[0][1:-1]
                        break
        logger.info("[GitBaseToolsLib] parse_patch parse email:{}".format(email_str))
        return email_str

    @classmethod
    def check_params(cls, list_data):
        """check parse params"""
        raise NotImplemented
