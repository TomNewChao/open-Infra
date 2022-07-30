# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:34
# @Author  : Tom_zc
# @FileName: scan_tools.py
# @Software: PyCharm
from open_infra.libs.obs_utils import ObsLib
from open_infra.utils.common import convert_yaml, output_scan_port_excel, output_scan_obs_excel
from open_infra.utils.scan_port import single_scan_port
from open_infra.utils.scan_obs import single_scan_obs
from django.conf import settings
from threading import Thread, Lock
from collections import defaultdict
from logging import getLogger
from open_infra.utils.scan_port import EipTools as ScanPortEipTools
from open_infra.utils.scan_obs import EipTools as ScanObsEipTools

logger = getLogger("django")


class LockObj(object):
    cloud_config = Lock()
    scan_port_lock = Lock()
    scan_obs_lock = Lock()


class BaseStatus(object):
    new = 0
    handler = 1
    finish = 2


class ScanPortStatus(BaseStatus):
    pass


class ScanObsStatus(BaseStatus):
    pass


class BaseInfo(object):
    _lock = Lock()
    _data = defaultdict(dict)

    @classmethod
    def set(cls, dict_data):
        with cls._lock:
            cls._data.update(dict_data)

    @classmethod
    def get(cls, key):
        with cls._lock:
            return cls._data.get(key)

    @classmethod
    def clear(cls):
        with cls._lock:
            cls._data = defaultdict(dict)

    @classmethod
    def delete_key(cls, key):
        with cls._lock:
            if key in cls._data.keys():
                del cls._data[key]


class ScanPortInfo(BaseInfo):
    pass


class ScanObsInfo(BaseInfo):
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
        account_list = ScanBaseTools.get_cloud_config()
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
    def get_cloud_config():
        obs_lib = ObsLib(settings.AK, settings.SK, settings.URL)
        content = obs_lib.get_obs_data(settings.DOWNLOAD_BUCKET_NAME, settings.DOWNLOAD_KEY_NAME)
        now_account_info_list = convert_yaml(content)
        return now_account_info_list

    def query_data(self, account_list):
        raise NotImplemented()


class ScanPorts(ScanBaseTools):
    def query_data(self, account_list):
        """query progress"""
        tcp_info, udp_info, tcp_server_info = dict(), dict(), dict()
        config_obj = self.get_cloud_config()
        print("#########################1:{}".format(config_obj))
        print("#########################2:{}".format(account_list))
        print("#########################3:{}".format(ScanPortInfo._data))
        for config_info in config_obj:
            if config_info["account"] not in account_list:
                continue
            ak = config_info["ak"]
            sk = config_info["sk"]
            for project_temp in config_info["project_info"]:
                project_id = project_temp["project_id"]
                zone = project_temp["zone"]
                key = (ak, sk, project_id, zone)
                print("#########################4:{}".format(key))
                scan_port_info = ScanPortInfo.get(key)
                if scan_port_info:
                    tcp_info.update(scan_port_info["data"]["tcp_info"])
                    udp_info.update(scan_port_info["data"]["udp_info"])
                    tcp_server_info.update(scan_port_info["data"]["tcp_server_info"])
        content = output_scan_port_excel(tcp_info, udp_info, tcp_server_info)
        return content


class ScanObs(ScanBaseTools):
    def query_data(self, account_list):
        anonymous_file_list, anonymous_bucket_list, anonymous_data_data = list(), list(), list()
        config_obj = self.get_cloud_config()
        for config_info in config_obj:
            account = config_info["account"]
            if account not in account_list:
                continue
            ak = config_info["ak"]
            sk = config_info["sk"]
            key = (ak, sk, account)
            scan_obs_info = ScanObsInfo.get(key)
            if scan_obs_info:
                anonymous_file_list.extend(scan_obs_info["data"]["anonymous_file"])
                anonymous_bucket_list.extend(scan_obs_info["data"]["anonymous_bucket"])
                anonymous_data_data.extend(scan_obs_info["data"]["anonymous_data"])
        return output_scan_obs_excel(anonymous_file_list, anonymous_bucket_list, anonymous_data_data)


class SingleScanPorts(ScanBaseTools):

    @staticmethod
    def collect_thread(ak, sk, zone, project_id):
        """collect data"""
        tcp_ret_dict, udp_ret_dict, tcp_server_info = single_scan_port(ak, sk, zone, project_id)
        dict_data = {
            "tcp_info": tcp_ret_dict,
            "udp_info": udp_ret_dict,
            "tcp_server_info": tcp_server_info
        }
        logger.info("collect_thread single scan port：{}".format(dict_data))
        key = (ak, sk, project_id, zone)
        ScanPortInfo.set({key: {"status": ScanPortStatus.finish, "data": dict_data}})

    def start_collect_thread(self, ak, sk, zone, project_id):
        """start a collect thread"""
        with LockObj.scan_port_lock:
            eip_tools = ScanPortEipTools()
            try:
                eip_tools.get_data_list(project_id, zone, ak, sk)
            except Exception as e:
                logger.error("param invalid:{}".format(e))
                return False
            # 1.judge status
            key = (ak, sk, project_id, zone)
            single_scan_port_info = ScanPortInfo.get(key)
            if single_scan_port_info is not None:
                return True
            # 2.start a thread to collect data
            th = Thread(target=self.collect_thread, args=(ak, sk, zone, project_id))
            th.start()
            # 3.set status to handler
            ScanPortInfo.set({key: {"status": ScanPortStatus.handler, "data": dict()}})
            return True

    # noinspection PyMethodMayBeStatic
    def query_progress(self, ak, sk, project_id, zone):
        """query progress"""
        content = str()
        key = (ak, sk, project_id, zone)
        single_scan_port_info = ScanPortInfo.get(key)
        print(key)
        print(ScanPortInfo._data)
        if single_scan_port_info is not None and single_scan_port_info["status"] == ScanPortStatus.handler:
            return 0, content
        elif single_scan_port_info is not None and single_scan_port_info["status"] == ScanPortStatus.finish:
            tcp_info = single_scan_port_info["data"]["tcp_info"]
            udp_info = single_scan_port_info["data"]["udp_info"]
            tcp_server_info = single_scan_port_info["data"]["tcp_server_info"]
            content = output_scan_port_excel(tcp_info, udp_info, tcp_server_info)
            return 1, content
        else:
            logger.info("single scan port query_progress query no result")
            return 2, content


class SingleScanObs(ScanBaseTools):
    _lock = Lock()

    @staticmethod
    def collect_thread(ak, sk, account):
        """collect data"""
        list_sensitive_file, list_anonymous_bucket, list_anonymous_data = single_scan_obs(ak, sk, account)
        dict_data = {
            "anonymous_file": list_sensitive_file or [],
            "anonymous_bucket": list_anonymous_bucket or [],
            "anonymous_data": list_anonymous_data or []
        }
        key = (ak, sk, account)
        logger.info("collect single scan_obs:{}".format(key))
        ScanObsInfo.set({key: {"status": ScanObsStatus.finish, "data": dict_data}})

    def start_collect_thread(self, ak, sk, account):
        """start a collect thread"""
        with LockObj.scan_obs_lock:
            try:
                eip_tools = ScanObsEipTools()
                eip_tools.get_all_bucket(ak, sk, settings.OBS_BASE_URL, inhibition_fault=False)
            except Exception as e:
                logger.error("start_collect_thread invalid param:{}".format(e))
                return False
            key = (ak, sk, account)
            # 1.judge status
            single_scan_obs_info = ScanObsInfo.get(key)
            if single_scan_obs_info is not None:
                return True
            # 2.start a thread to collect data
            th = Thread(target=self.collect_thread, args=(ak, sk, account))
            th.start()
            # 3.set status to handler
            ScanObsInfo.set({key: {"status": ScanObsStatus.handler, "data": dict()}})
            return True

    # noinspection PyMethodMayBeStatic
    def query_progress(self, ak, sk, account):
        """query progress"""
        content = str()
        key = (ak, sk, account)
        print(key)
        print(ScanObsInfo._data)
        single_scan_obs_info = ScanObsInfo.get(key)
        if single_scan_obs_info is not None and single_scan_obs_info["status"] == ScanObsStatus.handler:
            return 0, content
        elif single_scan_obs_info is not None and single_scan_obs_info["status"] == ScanObsStatus.finish:
            anonymous_file_list = single_scan_obs_info["data"]["anonymous_file"]
            anonymous_bucket_list = single_scan_obs_info["data"]["anonymous_bucket"]
            anonymous_data_data = single_scan_obs_info["data"]["anonymous_data"]
            content = output_scan_obs_excel(anonymous_file_list, anonymous_bucket_list, anonymous_data_data)
            return 1, content
        else:
            logger.info("single scan obs query_progress query no result")
            return 2, content
