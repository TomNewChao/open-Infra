# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:34
# @Author  : Tom_zc
# @FileName: scan_tools.py
# @Software: PyCharm
from open_infra.libs.obs_utils import ObsLib
from open_infra.utils.common import convert_yaml, output_scan_port_excel, output_scan_obs_excel
from open_infra.utils.scan_port import scan_port, single_scan_port
from open_infra.utils.scan_obs import scan_obs, single_scan_obs
from django.conf import settings
from threading import Thread, Lock
from collections import defaultdict
from logging import getLogger

logger = getLogger("django")


class BaseStatus(object):
    new = 0
    handler = 1
    finish = 2


class ScanPortStatus(BaseStatus):
    pass


class ScanObsStatus(BaseStatus):
    pass


class SingleScanPortStatus(BaseStatus):
    pass


class SingleScanObsStatus(BaseStatus):
    pass


class BaseInfo(object):
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


class ScanPortInfo(BaseInfo):
    pass


class ScanObsInfo(BaseInfo):
    pass


class SingleScanPortInfo(BaseInfo):
    pass


class SingleScanObsInfo(BaseInfo):
    pass


# noinspection PyArgumentList
class ScanBaseTools(object):
    _instance = None

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

    def start_collect_thread(self, account_list, username):
        raise NotImplemented()

    def query_progress(self, username):
        raise NotImplemented()


class ScanPorts(ScanBaseTools):
    _lock = Lock()

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
        logger.info("scan port：{}".format(dict_data))
        ScanPortInfo.set({username: {"status": ScanPortStatus.finish, "data": dict_data}})

    def start_collect_thread(self, account_list, username):
        """start a collect thread"""
        with self._lock:
            # 1.judge status
            scan_port_info = ScanPortInfo.get(username)
            if scan_port_info is not None and scan_port_info["status"] == ScanPortStatus.handler:
                return True
            # 2.delete tar info
            ScanPortInfo.delete_key(username)
            # 3.set status to new
            ScanPortInfo.set({username: {"status": ScanPortStatus.new, "data": dict()}})
            # 4.start a thread to collect data
            th = Thread(target=self.collect_thread, args=(account_list, username))
            th.start()
            # 5.set status to handler
            ScanPortInfo.set({username: {"status": ScanPortStatus.handler, "data": dict()}})

    def query_progress(self, username):
        """query progress"""
        with self._lock:
            content = str()
            scan_port_info = ScanPortInfo.get(username)
            print(scan_port_info)
            if scan_port_info is not None and scan_port_info["status"] == ScanPortStatus.handler:
                return 0, content
            elif scan_port_info is not None and scan_port_info["status"] == ScanPortStatus.finish:
                content = output_scan_port_excel(scan_port_info["data"])
                ScanPortInfo.delete_key(username)
                return 1, content
            else:
                logger.info("scan port query_progress query no result")
                return 2, content


class ScanObs(ScanBaseTools):
    _lock = Lock()

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
        list_sensitive_file, list_anonymous_bucket, list_anonymous_data = scan_obs(query_account_list)
        dict_data = {
            "file": list_sensitive_file,
            "bucket": list_anonymous_bucket,
            "data": list_anonymous_data
        }
        logger.info("collect scan_obs:{}".format(dict_data))
        ScanObsInfo.set({username: {"status": ScanObsStatus.finish, "data": dict_data}})

    def start_collect_thread(self, account_list, username):
        """start a collect thread"""
        with self._lock:
            # 1.judge status
            scan_obs_info = ScanObsInfo.get(username)
            if scan_obs_info is not None and scan_obs_info["status"] == ScanObsStatus.handler:
                return True
            # 2.delete tar info
            ScanObsInfo.delete_key(username)
            # 3.set status to new
            ScanObsInfo.set({username: {"status": ScanObsStatus.new, "data": dict()}})
            # 4.start a thread to collect data
            th = Thread(target=self.collect_thread, args=(account_list, username))
            th.start()
            # 5.set status to handler
            ScanObsInfo.set({username: {"status": ScanObsStatus.handler, "data": dict()}})

    def query_progress(self, username):
        """query progress"""
        with self._lock:
            content = str()
            scan_obs_info = ScanObsInfo.get(username)
            if scan_obs_info is not None and scan_obs_info["status"] == ScanObsStatus.handler:
                return 0, content
            elif scan_obs_info is not None and scan_obs_info["status"] == ScanObsStatus.finish:
                content = output_scan_obs_excel(scan_obs_info["data"])
                ScanObsInfo.delete_key(username)
                return 1, content
            else:
                logger.info("scan obs query_progress query no result")
                return 2, content


class SingleScanPorts(ScanBaseTools):
    _lock = Lock()

    @staticmethod
    def collect_thread(ak, sk, username, zone, project_id):
        """collect data"""
        tcp_ret_dict, udp_ret_dict, tcp_server_info = single_scan_port(ak, sk, username, zone, project_id)
        dict_data = {
            "tcp_info": tcp_ret_dict,
            "udp_info": udp_ret_dict,
            "tcp_server_info": tcp_server_info
        }
        logger.info("scan port：{}".format(dict_data))
        SingleScanPortInfo.set({username: {"status": ScanPortStatus.finish, "data": dict_data}})

    def start_collect_thread(self, ak, sk, username, zone, project_id):
        """start a collect thread"""
        with self._lock:
            # 1.judge status
            single_scan_port_info = SingleScanPortInfo.get(username)
            if single_scan_port_info is not None and single_scan_port_info["status"] == ScanPortStatus.handler:
                return True
            # 2.delete tar info
            SingleScanPortInfo.delete_key(username)
            # 3.set status to new
            SingleScanPortInfo.set({username: {"status": ScanPortStatus.new, "data": dict()}})
            # 4.start a thread to collect data
            th = Thread(target=self.collect_thread, args=(ak, sk, username, zone, project_id))
            th.start()
            # 5.set status to handler
            SingleScanPortInfo.set({username: {"status": ScanPortStatus.handler, "data": dict()}})

    def query_progress(self, username):
        """query progress"""
        with self._lock:
            content = str()
            single_scan_port_info = SingleScanPortInfo.get(username)
            if single_scan_port_info is not None and single_scan_port_info["status"] == ScanPortStatus.handler:
                return 0, content
            elif single_scan_port_info is not None and single_scan_port_info["status"] == ScanPortStatus.finish:
                content = output_scan_port_excel(single_scan_port_info["data"])
                SingleScanPortInfo.delete_key(username)
                return 1, content
            else:
                logger.info("single scan port query_progress query no result")
                return 2, content


class SingleScanObs(ScanBaseTools):
    _lock = Lock()

    @staticmethod
    def collect_thread(ak, sk, account, username):
        """collect data"""
        list_sensitive_file, list_anonymous_bucket, list_anonymous_data = singe_scan_obs(ak, sk, account)
        dict_data = {
            "file": list_sensitive_file,
            "bucket": list_anonymous_bucket,
            "data": list_anonymous_data
        }
        logger.info("collect single scan_obs:{}".format(dict_data))
        SingleScanObsInfo.set({username: {"status": ScanObsStatus.finish, "data": dict_data}})

    def start_collect_thread(self, ak, sk, account, username):
        """start a collect thread"""
        with self._lock:
            # 1.judge status
            single_scan_obs_info = SingleScanObsInfo.get(username)
            if single_scan_obs_info is not None and single_scan_obs_info["status"] == ScanObsStatus.handler:
                return True
            # 2.delete tar info
            SingleScanObsInfo.delete_key(username)
            # 3.set status to new
            SingleScanObsInfo.set({username: {"status": ScanObsStatus.new, "data": dict()}})
            # 4.start a thread to collect data
            th = Thread(target=self.collect_thread, args=(ak, sk, account, username))
            th.start()
            # 5.set status to handler
            SingleScanObsInfo.set({username: {"status": ScanObsStatus.handler, "data": dict()}})

    def query_progress(self, username):
        """query progress"""
        with self._lock:
            content = str()
            single_scan_obs_info = SingleScanObsInfo.get(username)
            if single_scan_obs_info is not None and single_scan_obs_info["status"] == ScanObsStatus.handler:
                return 0, content
            elif single_scan_obs_info is not None and single_scan_obs_info["status"] == ScanObsStatus.finish:
                content = output_scan_obs_excel(single_scan_obs_info["data"])
                ScanObsInfo.delete_key(username)
                return 1, content
            else:
                logger.info("single scan obs query_progress query no result")
                return 2, content
