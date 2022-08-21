# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 11:27
# @Author  : Tom_zc
# @FileName: scan_thread.py
# @Software: PyCharm
from clouds_tools.models import HWCloudAccount, HWCloudProjectInfo, HWCloudEipInfo
from clouds_tools.resources.scan_tools import ScanPortInfo, ScanObsInfo, ScanObsStatus, ScanBaseTools, ScanPortStatus
from open_infra.utils.common import func_retry
from open_infra.utils.scan_eip import get_eip_info
from open_infra.utils.scan_port import single_scan_port
from open_infra.utils.scan_obs import single_scan_obs
from logging import getLogger
from django.db import transaction

logger = getLogger("django")


class ScanToolsThread(object):
    @classmethod
    @func_retry()
    def query_account_info(cls):
        """query HWCloud account information: include zone and project id, refresh to database"""
        logger.info("----------------start query_account_info-----------------------")
        account_info_list = ScanBaseTools.get_hw_account_project_info_from_obs()
        with transaction.atomic():
            # 1.delete data
            HWCloudProjectInfo.objects.all().delete()
            HWCloudAccount.objects.all().delete()
            # 2.save data
            for account_info in account_info_list:
                account = account_info["account"]
                ak = account_info["ak"]
                sk = account_info["sk"]
                account_obj = HWCloudAccount.objects.create(account=account, ak=ak, sk=sk)
                for project_info in account_info["project_info"]:
                    project_id = project_info["project_id"]
                    zone = project_info["zone"]
                    HWCloudProjectInfo.objects.create(id=project_id, zone=zone, account=account_obj)
            # 3.clean memcached
            ScanBaseTools.account_info_list = list()
        logger.info("----------------finish query_account_info-----------------------")

    @classmethod
    @func_retry()
    def scan_eip(cls):
        logger.info("----------------start scan_eip-----------------------")
        account_info = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        eip_dict = get_eip_info(account_info)
        with transaction.atomic():
            HWCloudEipInfo.objects.all().delete()
            for account, eip_list in eip_dict.items():
                for eip_info in eip_list:
                    dict_data = {
                        "id": eip_info[2],
                        "eip": eip_info[0],
                        "eip_status": eip_info[3],
                        "eip_type": eip_info[4],
                        "bandwidth_id": eip_info[6],
                        "bandwidth_name": eip_info[5],
                        "bandwidth_size": eip_info[7],
                        "example_id": eip_info[10],
                        "example_name": eip_info[9],
                        "example_type": eip_info[8],
                        "eip_zone": eip_info[11],
                        "create_time": eip_info[12],
                        "account": account,
                    }
                    HWCloudEipInfo.objects.create(**dict_data)
        logger.info("----------------finish scan_eip-----------------------")

    @classmethod
    @func_retry()
    def scan_port(cls):
        logger.info("----------------start scan_port-----------------------")
        ScanPortInfo.clear()
        now_account_info_list = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        for config_item in now_account_info_list:
            ak = config_item["ak"]
            sk = config_item["sk"]
            project_list = config_item["project_info"]
            for project_info in project_list:
                project_id = project_info.get("project_id")
                zone = project_info.get("zone")
                key = (ak, sk, project_id, zone)
                single_scan_port_info = ScanPortInfo.get(key)
                if single_scan_port_info is not None:
                    continue
                ScanPortInfo.set({key: {"status": ScanPortStatus.new, "data": dict()}})
                tcp_ret_dict, udp_ret_dict, tcp_server_info = single_scan_port(ak, sk, zone, project_id)
                dict_data = {
                    "tcp_info": tcp_ret_dict,
                    "udp_info": udp_ret_dict,
                    "tcp_server_info": tcp_server_info
                }
                logger.info(
                    "[ScanThreadTools] scan_port: key:({},{},{},{}), data:{}".format(ak[0:5], sk[0:5], project_id, zone,
                                                                                     dict_data))
                ScanPortInfo.set({key: {"status": ScanPortStatus.finish, "data": dict_data}})
        logger.info("----------------finish scan_port-----------------------")

    @classmethod
    @func_retry()
    def scan_obs(cls):
        logger.info("----------------start scan_obs-----------------------")
        ScanObsInfo.clear()
        now_account_info_list = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        for config_item in now_account_info_list:
            ak = config_item["ak"]
            sk = config_item["sk"]
            account = config_item["account"]
            key = (ak, sk, account)
            single_scan_obs_info = ScanObsInfo.get(key)
            if single_scan_obs_info is not None:
                continue
            ScanObsInfo.set({key: {"status": ScanObsStatus.new, "data": dict()}})
            file_list, bucket_list, data_list = single_scan_obs(ak, sk, account)
            dict_data = {
                "anonymous_file": file_list or [],
                "anonymous_bucket": bucket_list or [],
                "anonymous_data": data_list or []
            }
            logger.info("[ScanThreadTools] scan_obs:({},{},{}),data：{}".format(ak[0:5], sk[0:5], account, dict_data))
            ScanObsInfo.set({key: {"status": ScanObsStatus.finish, "data": dict_data}})
        logger.info("----------------finish scan_obs-----------------------")

    @classmethod
    def refresh_data(cls):
        # cls.query_account_info()
        # cls.scan_eip()
        # cls.scan_port()
        # cls.scan_obs()
        pass
