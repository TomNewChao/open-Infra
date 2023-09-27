# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:34
# @Author  : Tom_zc
# @FileName: scan_tools.py
# @Software: PyCharm
import traceback

from django.db import transaction
from django.conf import settings
from threading import Thread, Lock
from logging import getLogger

from app_resources.resources.account_mgr import AccountMgr
from app_tools.models import HWCloudScanEipPortInfo, HWCloudScanEipPortStatus, HWCloudScanObsAnonymousBucket, \
    HWCloudScanObsAnonymousFile, HWCloudScanObsAnonymousStatus, HWCloudHighRiskPort
from app_tools.resources.constants import NetProtocol, ScanToolsLock, ScanPortStatus, ScanObsStatus
from open_infra.libs.lib_cloud import HWCloudIAM
from open_infra.utils.common import output_scan_port_excel, output_scan_obs_excel, get_suitable_range
from open_infra.utils.default_port_list import HighRiskPort
from open_infra.tools.scan_port import scan_port
from open_infra.tools.scan_obs import ObsTools, scan_obs

logger = getLogger("django")


class ScanToolsMgr(object):
    @staticmethod
    def save_scan_eip_port_info_status(tcp_info, udp_info, account_list, creating=True):
        if not isinstance(account_list, list):
            raise Exception("[save_scan_eip_port_info_status] account_list must be list")
        for ip, port_list in tcp_info.items():
            for port_info in port_list:
                dict_data = {
                    "eip": ip,
                    "port": port_info[0],
                    "status": port_info[1],
                    "link_protocol": port_info[2],
                    "transport_protocol": port_info[3],
                    "account": port_info[4],
                    "region": port_info[5],
                    "service_info": port_info[6],
                    "protocol": NetProtocol.TCP
                }
                HWCloudScanEipPortInfo.create_single(**dict_data)
        for ip, port_list in udp_info.items():
            for port_info in port_list:
                dict_data = {
                    "eip": ip,
                    "port": port_info[0],
                    "status": port_info[1],
                    "link_protocol": port_info[2],
                    "transport_protocol": port_info[3],
                    "account": port_info[4],
                    "region": port_info[5],
                    "service_info": "",
                    "protocol": NetProtocol.UDP
                }
                HWCloudScanEipPortInfo.create_single(**dict_data)
        if creating:
            status_list = [HWCloudScanEipPortStatus(account=account, status=ScanPortStatus.finish)
                           for account in account_list]
            HWCloudScanEipPortStatus.create_all(status_list)
        else:
            HWCloudScanEipPortStatus.update_status(account_list, ScanPortStatus.finish)

    @staticmethod
    def save_scan_obs_info_status(list_anonymous_bucket, list_anonymous_file, account_list, creating=True):
        for anonymous_data in list_anonymous_bucket:
            dict_data = {
                "account": anonymous_data[0],
                "bucket": anonymous_data[1],
                "url": anonymous_data[2],
            }
            HWCloudScanObsAnonymousBucket.create_single(**dict_data)
        for anonymous_data in list_anonymous_file:
            dict_data = {
                "account": anonymous_data[0],
                "bucket": anonymous_data[1],
                "url": anonymous_data[2],
                "path": anonymous_data[3],
                "data": anonymous_data[4],
            }
            HWCloudScanObsAnonymousFile.create_single(**dict_data)
        if creating:
            status_list = [HWCloudScanObsAnonymousStatus(account=account, status=ScanObsStatus.finish)
                           for account in account_list]
            HWCloudScanObsAnonymousStatus.create_all(status_list)
        else:
            HWCloudScanObsAnonymousStatus.get(account_list, ScanObsStatus.finish)


# noinspection PyArgumentList
class ScanBaseTools(object):
    _instance = None

    account_info_list = list()
    sla_yaml_list = list()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def get_random_cloud_config(ak, sk):
        return HWCloudIAM(ak, sk).get_project_zone()

    @staticmethod
    def get_project_info(ak, sk):
        clouds_config = AccountMgr.get_decrypt_hw_account_project_info_from_database()
        for cloud_info in clouds_config:
            if cloud_info["ak"] == ak and cloud_info["sk"] == sk:
                return cloud_info["project_info"]
        return list()

    @staticmethod
    def parse_scan_eip_query_info(eip_list):
        tcp_list, udp_list = list(), list()
        for eip_info in eip_list:
            if eip_info.protocol == NetProtocol.TCP:
                tcp_list.append(list(eip_info.to_dict().values())[1:-1])
            elif eip_info.protocol == NetProtocol.UDP:
                udp_list.append(list(eip_info.to_dict().values())[1:-1])
        content = output_scan_port_excel(tcp_list, udp_list)
        return content

    @staticmethod
    def parse_scan_obs_query_info(query_account):
        anonymous_bucket_list, anonymous_file_list, anonymous_data_list = list(), list(), list()
        if isinstance(query_account, list):
            anonymous_bucket_temp = HWCloudScanObsAnonymousBucket.filter_account(query_account)
            anonymous_file_temp = HWCloudScanObsAnonymousFile.filter_account(query_account)
        else:
            anonymous_bucket_temp = HWCloudScanObsAnonymousBucket.equal_account(query_account)
            anonymous_file_temp = HWCloudScanObsAnonymousFile.equal_account(query_account)
        anonymous_bucket_list.extend([list(data.to_dict().values())[1:] for data in anonymous_bucket_temp])
        anonymous_file_list.extend([list(data.to_dict().values())[1:] for data in anonymous_file_temp])
        return output_scan_obs_excel(anonymous_file_list, anonymous_bucket_list)

    @staticmethod
    def get_account_dict(ak, sk, account):
        account_dict = dict()
        project_info = ScanBaseTools.get_random_cloud_config(ak, sk)
        if not project_info:
            raise Exception("[start_collect_thread] Get empty project info, Failed")
        account_dict["account"] = account
        account_dict["ak"] = ak
        account_dict["sk"] = sk
        account_dict["project_info"] = project_info
        return account_dict


class ScanPortsMgr(ScanToolsMgr):
    def query_data(self, account_list):
        """query progress"""
        config_obj = AccountMgr.get_decrypt_hw_account_project_info_from_database()
        query_account = list()
        for config_info in config_obj:
            if config_info["account"] in account_list:
                query_account.append(config_info["account"])
        eip_list = HWCloudScanEipPortInfo.filter_account(query_account)
        return ScanBaseTools.parse_scan_eip_query_info(eip_list)


class SingleScanPortsMgr(ScanToolsMgr):

    @staticmethod
    def collect_thread(account_list):
        """collect data"""
        tcp_info, udp_info, account_name_list = scan_port(account_list)
        with transaction.atomic():
            ScanToolsMgr.save_scan_eip_port_info_status(tcp_info, udp_info, account_name_list, creating=False)
        logger.info("[collect_thread] collect high risk port, account:{}".format(account_list[0]["account"]))

    def start_collect_thread(self, ak, sk, account):
        """start a collect thread"""
        try:
            account_dict = ScanBaseTools.get_account_dict(ak, sk, account)
        except Exception as e:
            logger.error("[start_collect_thread] connect:{}, {}".format(e, traceback.format_exc()))
            return 0
        is_blocking = ScanToolsLock.scan_port.acquire(blocking=False)
        if not is_blocking:
            return 1
        try:
            account_status = HWCloudScanEipPortStatus.query_scan_eip_port_status(account)
            if account_status:
                return 2
            HWCloudScanEipPortStatus.save_scan_eip_port_status(account=account, status=ScanPortStatus.handler)
            th = Thread(target=self.collect_thread, args=([account_dict],))
            th.start()
            return 2
        finally:
            ScanToolsLock.scan_port.release()

    # noinspection PyMethodMayBeStatic
    def query_progress(self, account):
        """query progress"""
        content = str()
        account_status = HWCloudScanEipPortStatus.query_scan_eip_port_status(account)
        if not account_status:
            return 0, content
        if account_status.status == ScanPortStatus.handler:
            return 0, content
        eip_list = HWCloudScanEipPortInfo.equal_account(account)
        content = ScanBaseTools.parse_scan_eip_query_info(eip_list)
        return 1, content


class ScanObsMgr(ScanToolsMgr):
    def query_data(self, account_list):
        config_obj = AccountMgr.get_decrypt_hw_account_project_info_from_database()
        query_account = list()
        for config_info in config_obj:
            account = config_info["account"]
            if account in account_list:
                query_account.append(account)
        return ScanBaseTools.parse_scan_obs_query_info(query_account)


class SingleScanObsMgr(ScanToolsMgr):

    @staticmethod
    def collect_thread(account_dict_list):
        """collect data"""
        list_anonymous_bucket, list_sensitive_file, account_list = scan_obs(account_dict_list)
        with transaction.atomic():
            ScanToolsMgr.save_scan_obs_info_status(list_anonymous_bucket, list_sensitive_file, account_list,
                                                   creating=False)

    def start_collect_thread(self, ak, sk, account):
        """start a collect thread"""
        try:
            eip_tools = ObsTools()
            eip_tools.get_all_bucket(ak, sk, settings.OBS_BASE_URL, inhibition_fault=False)
            account_dict = ScanBaseTools.get_account_dict(ak, sk, account)
        except Exception as e:
            logger.error("[SingleScanObs] start_collect_thread connect:{}, {}".format(e, traceback.format_exc()))
            return 0
        is_blocking = ScanToolsLock.scan_obs.acquire(blocking=False)
        if not is_blocking:
            return 1
        try:
            account_status = HWCloudScanObsAnonymousStatus.query_scan_obs_status(account)
            if account_status:
                return 2
            HWCloudScanObsAnonymousStatus.save_scan_obs_status(account, ScanObsStatus.handler)
            th = Thread(target=self.collect_thread, args=([account_dict],))
            th.start()
            return 2
        finally:
            ScanToolsLock.scan_obs.release()

    # noinspection PyMethodMayBeStatic
    def query_progress(self, account):
        """query progress"""
        content = str()
        account_status = HWCloudScanObsAnonymousStatus.query_scan_obs_status(account)
        if not account_status:
            return 0, content
        if account_status.status == ScanObsStatus.handler:
            return 0, content
        content = ScanBaseTools.parse_scan_obs_query_info(account)
        return 1, content


# noinspection PyMethodMayBeStatic
class HighRiskPortMgr(ScanToolsMgr):
    _create_lock = Lock()

    def list(self, kwargs):
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        if filter_name and filter_name == "port":
            eip_list = HWCloudHighRiskPort.filter(filter_value)
        else:
            eip_list = HWCloudHighRiskPort.all()
        total = len(eip_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "create_time"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        eip_list = eip_list.order_by(order_by)
        task_list = [task.to_dict() for task in eip_list[slice_obj]]
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": task_list
        }
        return res

    def create(self, port, desc):
        with HighRiskPortMgr._create_lock:
            if HWCloudHighRiskPort.query_high_risk_port(port):
                return 1
            HWCloudHighRiskPort.create_single(port=port, desc=desc)
            HighRiskPort.cur_port_dict.update({port: desc})
            return 0

    def delete(self, port_list):
        HWCloudHighRiskPort.delete_single(port_list)
        for port in port_list:
            if port in HighRiskPort.cur_port_dict.keys():
                del HighRiskPort.cur_port_dict[port]
        return True
