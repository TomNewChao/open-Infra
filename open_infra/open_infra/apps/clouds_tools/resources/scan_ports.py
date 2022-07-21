# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:34
# @Author  : Tom_zc
# @FileName: scan_ports.py
# @Software: PyCharm
import datetime
import os
import tempfile

from open_infra.libs.obs_utils import ObsLib
from open_infra.utils.common import convert_yaml, output_excel
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
        tcp_ret_dict, udp_ret_dict, tcp_server_info = scan_port(query_account_list)
        dict_data = {
            "tcp_info": tcp_ret_dict,
            "udp_info": udp_ret_dict,
            "tcp_server_info": tcp_server_info
        }
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
        with tempfile.NamedTemporaryFile() as out_tmp_file:
            now_date = datetime.datetime.now()
            full_path = os.path.join(out_tmp_file.name, settings.EXCEL_NAME.format(username, now_date))
            output_excel(full_path, scan_port_info["tcp_info"], settings.EXCEL_TCP_PAGE_NAME, settings.EXCEL_TITLE)
            output_excel(full_path, scan_port_info["udp_info"], settings.EXCEL_UDP_PAGE_NAME, settings.EXCEL_TITLE)
            output_excel(full_path, scan_port_info["tcp_server_info"], settings.EXCEL_SERVER_PAGE_NAME,
                         settings.EXCEL_SERVER_TITLE)
            with open(full_path, "rb") as f:
                return f.readline()

    def query_progress(self, username):
        """query progress"""
        with self._lock:
            content = str()
            scan_port_info = ScanPortInfo.get(username)
            if scan_port_info is not None and scan_port_info["status"] == ScanPortStatus.handler:
                return 0, content
            elif scan_port_info is not None and scan_port_info["status"] == ScanPortStatus.finish:
                content = self.get_excel_content(scan_port_info["data"])
                ScanPortInfo.delete_key(username)
                return 1, content
            else:
                logger.info("query_progress query no result")
                return 2, content
