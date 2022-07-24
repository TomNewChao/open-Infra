# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:34
# @Author  : Tom_zc
# @FileName: scan_ports.py
# @Software: PyCharm
import datetime
import os
import shutil
import uuid

from open_infra.libs.obs_utils import ObsLib
from open_infra.utils.common import convert_yaml, output_all_excel
from open_infra.utils.scan_port import scan_port
from django.conf import settings
from threading import Thread, Lock
from collections import defaultdict
from logging import getLogger

logger = getLogger("django")


class ScanPortStatus(object):
    new = 0
    handler = 1
    finish = 2


class ScanPortInfo(object):
    _lock = Lock()
    _data = defaultdict(dict)

    @classmethod
    def set(cls, dict_data):
        with cls._lock:
            cls._data.update(dict_data)

    @classmethod
    def get(cls, username):
        with cls._lock:
            return cls._data.get(username)

    @classmethod
    def delete_key(cls, username):
        with cls._lock:
            if username in cls._data.keys():
                del cls._data[username]


# noinspection PyArgumentList
class ScanPorts(object):
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def get_cloud_account():
        """get all cloud account"""
        obs_lib = ObsLib(settings.AK, settings.SK, settings.URL)
        content = obs_lib.get_obs_data(settings.DOWNLOAD_BUCKET_NAME, settings.DOWNLOAD_KEY_NAME)
        account_list = convert_yaml(content)
        ret_list = list()
        for account_info in account_list:
            account_temp = dict()
            account_temp["account"] = account_info["account"]
            zone_list = [settings.ZONE_ALIAS_DICT.get(project_temp["zone"], "UNKNOWN") for project_temp in
                         account_info["project_info"]]
            account_temp["zone"] = "，".join(zone_list)
            ret_list.append(account_temp)
        return ret_list

    @staticmethod
    def collect_thread(account_list, username):
        """collect data"""
        obs_lib = ObsLib(settings.AK, settings.SK, settings.URL)
        content = obs_lib.get_obs_data(settings.DOWNLOAD_BUCKET_NAME, settings.DOWNLOAD_KEY_NAME)
        now_account_info_list = convert_yaml(content)
        query_account_list = list()
        for account_info in now_account_info_list:
            if account_info["account"] in account_list:
                query_account_list.append(account_info)
        tcp_ret_dict, udp_ret_dict, tcp_server_info = scan_port(username, query_account_list)
        dict_data = {
            "tcp_info": tcp_ret_dict,
            "udp_info": udp_ret_dict,
            "tcp_server_info": tcp_server_info
        }
        print(dict_data)
        ScanPortInfo.set({username: {"status": ScanPortStatus.finish, "data": dict_data}})

    def start_collect_thread(self, account_list, username):
        """start a collect thread"""
        with self._lock:
            # 1.judge status
            scan_port_info = ScanPortInfo.get(username)
            if scan_port_info is not None and scan_port_info["status"] == ScanPortStatus.handler:
                return True
            # 2.set status to new
            ScanPortInfo.set({username: {"status": ScanPortStatus.new, "data": dict()}})
            # 3.delete tar info
            ScanPortInfo.delete_key(username)
            # 4.start a thread to collect data
            th = Thread(target=self.collect_thread, args=(account_list, username))
            th.start()
            # 5.set status to handler
            ScanPortInfo.set({username: {"status": ScanPortStatus.handler, "data": dict()}})

    @staticmethod
    def get_excel_content(scan_port_info, username):
        """get excel content"""
        if not username:
            username = "anonymous_{}".format(uuid.uuid1())
        now_date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = "IP端口扫描统计表_{}.xlsx".format(now_date)
        content = output_all_excel(scan_port_info)
        return file_name, content

    def query_progress(self, username):
        """query progress"""
        with self._lock:
            content, filename = str(), str()
            scan_port_info = ScanPortInfo.get(username)
            if scan_port_info is not None and scan_port_info["status"] == ScanPortStatus.handler:
                return 0, filename, content
            elif scan_port_info is not None and scan_port_info["status"] == ScanPortStatus.finish:
                filename, content = self.get_excel_content(scan_port_info["data"], username)
                # ScanPortInfo.delete_key(username)
                return 1, filename, content
            else:
                logger.info("query_progress query no result")
                return 2, filename, content
