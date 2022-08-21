# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:34
# @Author  : Tom_zc
# @FileName: scan_tools.py
# @Software: PyCharm
import traceback

from clouds_tools.models import HWCloudProjectInfo, HWCloudAccount, HWCloudEipInfo
from open_infra.libs.obs_utils import ObsLib, HWCloudIAM
from open_infra.utils.common import output_scan_port_excel, output_scan_obs_excel
from open_infra.utils.crypto import AESCrypt
from open_infra.utils.scan_port import single_scan_port
from open_infra.utils.scan_obs import single_scan_obs
from django.conf import settings
from threading import Thread, Lock
from collections import defaultdict
from logging import getLogger
from open_infra.utils.scan_port import EipTools as ScanPortEipTools
from open_infra.utils.scan_obs import EipTools as ScanObsEipTools

logger = getLogger("django")


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
    _aes_crypt = AESCrypt()
    account_info_list = list()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def get_hw_account_from_obs():
        obs_lib = ObsLib(settings.AK, settings.SK, settings.URL)
        content = obs_lib.get_obs_data(settings.DOWNLOAD_BUCKET_NAME, settings.DOWNLOAD_KEY_NAME)
        return content

    @classmethod
    def get_hw_project_info_from_obs(cls, now_account_info_list):
        if not isinstance(now_account_info_list, list):
            raise Exception("now_account_info_list must be list")
        for account_info in now_account_info_list:
            account_info["project_info"] = HWCloudIAM.get_project_zone(account_info["ak"], account_info["sk"])

    @classmethod
    def handle_sensitive_data(cls, account_list):
        for account_info in account_list:
            account_info["ak"] = cls._aes_crypt.encrypt(account_info["ak"])
            account_info["sk"] = cls._aes_crypt.encrypt(account_info["sk"])

    @classmethod
    def get_hw_account_project_info_from_obs(cls):
        content = cls.get_hw_account_from_obs()
        cls.get_hw_project_info_from_obs(content)
        cls.handle_sensitive_data(content)
        # return content
        #  it is for test
        list_data = list()
        for data in content:
            if data["account"] == "hwstaff_zengchen1024":
                list_data.append(data)
        return list_data

    @classmethod
    def get_hw_account_project_info_from_database(cls):
        account_list = list()
        account_info_list = HWCloudAccount.objects.all()
        for account_info in account_info_list:
            account_info_dict = account_info.to_dict()
            project_info_list = HWCloudProjectInfo.objects.filter(account__id=account_info_dict["id"])
            account_info_dict["project_info"] = [{"project_id": project_info.id, "zone": project_info.zone} for
                                                 project_info in project_info_list]
            account_list.append(account_info_dict)
        return account_list

    @classmethod
    def handle_encrypt_data(cls, account_list):
        for account_info in account_list:
            account_info["ak"] = cls._aes_crypt.decrypt(account_info["ak"])
            account_info["sk"] = cls._aes_crypt.decrypt(account_info["sk"])

    @classmethod
    def get_decrypt_hw_account_project_info_from_database(cls):
        if not cls.account_info_list:
            account_list = cls.get_hw_account_project_info_from_database()
            cls.handle_encrypt_data(account_list)
            cls.account_info_list = account_list
        return cls.account_info_list

    @staticmethod
    def get_random_cloud_config(ak, sk):
        return HWCloudIAM.get_project_zone(ak, sk)

    @staticmethod
    def get_project_info(ak, sk):
        clouds_config = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        for cloud_info in clouds_config:
            if cloud_info["ak"] == ak and cloud_info["sk"] == sk:
                return cloud_info["project_info"]
        return list()


class ScanToolsMgr:
    scan_base_tools = ScanBaseTools()

    @staticmethod
    def get_cloud_account():
        """get all cloud account"""
        account_list = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        ret_list = list()
        for account_info in account_list:
            account_temp = dict()
            account_temp["account"] = account_info["account"]
            zone_list = [settings.ZONE_ALIAS_DICT.get(project_temp["zone"], project_temp['zone']) for project_temp in
                         account_info["project_info"]]
            account_temp["zone"] = "，".join(zone_list)
            ret_list.append(account_temp)
        return ret_list


class ScanPortsMgr(ScanToolsMgr):
    def query_data(self, account_list):
        """query progress"""
        tcp_info, udp_info, tcp_server_info = dict(), dict(), dict()
        config_obj = self.scan_base_tools.get_decrypt_hw_account_project_info_from_database()
        for config_info in config_obj:
            if config_info["account"] not in account_list:
                continue
            ak = config_info["ak"]
            sk = config_info["sk"]
            for project_temp in config_info["project_info"]:
                project_id = project_temp["project_id"]
                zone = project_temp["zone"]
                key = (ak, sk, project_id, zone)
                scan_port_info = ScanPortInfo.get(key)
                logger.error(
                    "[ScanPorts:query_data]: key:({}, {}, {}, {}), value:{}".format(ak[:5], sk[:5], project_id, zone,
                                                                                    scan_port_info))
                if scan_port_info and scan_port_info["status"] == ScanPortStatus.finish:
                    tcp_info.update(scan_port_info["data"]["tcp_info"])
                    udp_info.update(scan_port_info["data"]["udp_info"])
                    tcp_server_info.update(scan_port_info["data"]["tcp_server_info"])
        content = output_scan_port_excel(tcp_info, udp_info, tcp_server_info)
        return content


class ScanObsMgr(ScanToolsMgr):
    def query_data(self, account_list):
        anonymous_file_list, anonymous_bucket_list, anonymous_data_data = list(), list(), list()
        config_obj = self.scan_base_tools.get_decrypt_hw_account_project_info_from_database()
        for config_info in config_obj:
            account = config_info["account"]
            if account not in account_list:
                continue
            ak = config_info["ak"]
            sk = config_info["sk"]
            key = (ak, sk, account)
            scan_obs_info = ScanObsInfo.get(key)
            logger.error(
                "[ScanObs:query_data]: key:({}, {}, {}), value:{}".format(ak[:5], sk[:5], account, scan_obs_info))
            if scan_obs_info and scan_obs_info["status"] == ScanObsStatus.finish:
                anonymous_file_list.extend(scan_obs_info["data"]["anonymous_file"])
                anonymous_bucket_list.extend(scan_obs_info["data"]["anonymous_bucket"])
                anonymous_data_data.extend(scan_obs_info["data"]["anonymous_data"])
        return output_scan_obs_excel(anonymous_file_list, anonymous_bucket_list, anonymous_data_data)


class SingleScanPortsMgr(ScanToolsMgr):

    @staticmethod
    def collect_thread(ak, sk, zone, project_id):
        """collect data"""
        tcp_ret_dict, udp_ret_dict, tcp_server_info = single_scan_port(ak, sk, zone, project_id)
        dict_data = {
            "tcp_info": tcp_ret_dict,
            "udp_info": udp_ret_dict,
            "tcp_server_info": tcp_server_info
        }
        key = (ak, sk, project_id, zone)
        logger.info("[collect_thread] collect single scan port: key:({}, {}, {}, {}), data:{}".format(ak[:5], sk[:5],
                                                                                                      project_id, zone,
                                                                                                      dict_data))
        ScanPortInfo.set({key: {"status": ScanPortStatus.finish, "data": dict_data}})

    def start_collect_thread(self, ak, sk):
        """start a collect thread"""
        eip_tools = ScanPortEipTools()
        try:
            project_info = ScanBaseTools.get_random_cloud_config(ak, sk)
            if not project_info:
                raise Exception("[start_collect_thread] Get empty project info, Failed")
            for project_obj in project_info:
                eip_tools.get_data_list(project_obj["project_id"], project_obj["zone"], ak, sk)
                break
        except Exception as e:
            logger.error("[start_collect_thread] connect:{}, {}".format(e, traceback.format_exc()))
            return False
        for project_obj in project_info:
            try:
                # 1.judge status
                project_id = project_obj["project_id"]
                zone = project_obj["zone"]
                key = (ak, sk, project_id, zone)
                single_scan_port_info = ScanPortInfo.get(key)
                if single_scan_port_info is not None:
                    continue
                ScanPortInfo.set({key: {"status": ScanPortStatus.new, "data": dict()}})
                # 2.start a thread to collect data
                th = Thread(target=self.collect_thread, args=(ak, sk, zone, project_id))
                th.start()
                # 3.set status to handler
                ScanPortInfo.set({key: {"status": ScanPortStatus.handler, "data": dict()}})
            except Exception as e:
                logger.error(
                    "[start_collect_thread] collect data failed:{}, traceback:{}".format(e, traceback.format_exc()))
        return True

    # noinspection PyMethodMayBeStatic
    def query_progress(self, ak, sk):
        """query progress"""
        tcp_info, udp_info, tcp_server_info = dict(), dict(), dict()
        content = str()
        project_info = ScanBaseTools.get_random_cloud_config(ak, sk)
        if not project_info:
            return 0, content
        for project_obj in project_info:
            project_id = project_obj["project_id"]
            zone = project_obj["zone"]
            key = (ak, sk, project_id, zone)
            single_scan_port_info = ScanPortInfo.get(key)
            if single_scan_port_info is not None and single_scan_port_info["status"] == ScanObsStatus.handler:
                return 0, content
            elif single_scan_port_info is not None and single_scan_port_info["status"] == ScanPortStatus.finish:
                tcp_info.update(single_scan_port_info["data"]["tcp_info"])
                udp_info.update(single_scan_port_info["data"]["udp_info"])
                tcp_server_info.update(single_scan_port_info["data"]["tcp_server_info"])
        content = output_scan_port_excel(tcp_info, udp_info, tcp_server_info)
        return 1, content


class SingleScanObsMgr(ScanToolsMgr):
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
        logger.info("[SingleScanObs] collect single scan_obs: key({},{},{}), data:{}".format(ak[:5], sk[:5], account,
                                                                                             dict_data))
        ScanObsInfo.set({key: {"status": ScanObsStatus.finish, "data": dict_data}})

    def start_collect_thread(self, ak, sk, account):
        """start a collect thread"""
        try:
            eip_tools = ScanObsEipTools()
            eip_tools.get_all_bucket(ak, sk, settings.OBS_BASE_URL, inhibition_fault=False)
        except Exception as e:
            logger.error("[SingleScanObs] start_collect_thread connect:{}, {}".format(e, traceback.format_exc()))
            return False
        key = (ak, sk, account)
        # 1.judge status
        single_scan_obs_info = ScanObsInfo.get(key)
        if single_scan_obs_info is not None:
            return True
        ScanObsInfo.set({key: {"status": ScanObsStatus.new, "data": dict()}})
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
        single_scan_obs_info = ScanObsInfo.get(key)
        if single_scan_obs_info is not None and single_scan_obs_info["status"] == ScanObsStatus.handler:
            return 0, content
        if single_scan_obs_info is not None and single_scan_obs_info["status"] == ScanObsStatus.finish:
            anonymous_file_list = single_scan_obs_info["data"]["anonymous_file"]
            anonymous_bucket_list = single_scan_obs_info["data"]["anonymous_bucket"]
            anonymous_data_data = single_scan_obs_info["data"]["anonymous_data"]
            content = output_scan_obs_excel(anonymous_file_list, anonymous_bucket_list, anonymous_data_data)
            return 1, content
        else:
            logger.info("single scan obs query_progress query no result")
            return 2, content


class EipMgr(ScanToolsMgr):
    def list_eip(self):
        eip_list = HWCloudEipInfo.objects.all()
        return [eip_info.to_dict() for eip_info in eip_list]
