# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 11:27
# @Author  : Tom_zc
# @FileName: scan_thread.py
# @Software: PyCharm
import datetime

from clouds_tools.models import HWCloudAccount, HWCloudProjectInfo, HWCloudEipInfo, HWCloudScanEipPortInfo, \
    HWCloudScanEipPortStatus, HWCloudScanObsAnonymousStatus, HWCloudScanObsAnonymousBucket, HWCloudScanObsAnonymousFile, \
    HWCloudHighRiskPort
from clouds_tools.resources.constants import ScanToolsLock
from clouds_tools.resources.scan_tools import ScanBaseTools, ScanOrmTools
from open_infra.utils import scan_obs
from open_infra.utils.common import func_retry
from open_infra.utils.default_port_list import HighRiskPort
from open_infra.utils.scan_eip import get_eip_info
from open_infra.utils.scan_port import scan_port
from open_infra.utils.scan_obs import scan_obs
from logging import getLogger
from django.db import transaction

logger = getLogger("django")


class ScanToolsThread(object):
    @classmethod
    @func_retry()
    def query_account_info(cls):
        """query HWCloud account information: include zone and project id, refresh to database"""
        logger.info("----------------1.start query_account_info-----------------------")
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
        logger.info("----------------1.finish query_account_info-----------------------")

    @classmethod
    def scan_eip(cls):
        logger.info("----------------2.start scan_eip-----------------------")
        account_info = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        eip_dict = get_eip_info(account_info)
        with transaction.atomic():
            HWCloudEipInfo.objects.all().delete()
            cur_datetime = datetime.datetime.now()
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
                        "refresh_time": cur_datetime,
                    }
                    HWCloudEipInfo.objects.create(**dict_data)
        logger.info("----------------2.finish scan_eip-----------------------")

    @classmethod
    def scan_sla(cls):
        logger.info("----------------3.start scan_sla-----------------------")
        ScanBaseTools.sla_yaml_list = list()
        logger.info("----------------3.finish scan_sla-----------------------")

    @classmethod
    def scan_port(cls):
        logger.info("----------------1.start scan_port-----------------------")
        now_account_info_list = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        tcp_info, udp_info, account_list = scan_port(now_account_info_list)
        with transaction.atomic():
            HWCloudScanEipPortInfo.objects.all().delete()
            HWCloudScanEipPortStatus.objects.all().delete()
            ScanOrmTools.save_scan_eip_port_info_status(tcp_info, udp_info, account_list)
            HighRiskPort.cur_port_list = None
        logger.info("----------------1.finish scan_port-----------------------")

    @classmethod
    def scan_obs(cls):
        logger.info("----------------2.start scan_obs-----------------------")
        now_account_info_list = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        list_anonymous_bucket, list_anonymous_file, account_list = scan_obs(now_account_info_list)
        with transaction.atomic():
            HWCloudScanObsAnonymousStatus.objects.all().delete()
            HWCloudScanObsAnonymousBucket.objects.all().delete()
            HWCloudScanObsAnonymousFile.objects.all().delete()
            ScanOrmTools.save_scan_obs_info_status(list_anonymous_bucket, list_anonymous_file, account_list)
        logger.info("----------------2.finish scan_obs-----------------------")

    @classmethod
    def immediately_cron_job(cls):
        cls.query_account_info()
        cls.scan_eip()
        cls.scan_sla()

    @classmethod
    def cron_job(cls):
        try:
            ScanToolsLock.scan_port.acquire()
            cls.scan_port()
        finally:
            ScanToolsLock.scan_port.release()
        try:
            ScanToolsLock.scan_obs.acquire()
            cls.scan_obs()
        finally:
            ScanToolsLock.scan_obs.release()
        pass

    @classmethod
    @func_retry()
    def scan_high_level_port(cls):
        logger.info("----------------1.start scan high level port-----------------")
        default_port_dict = HighRiskPort.get_port_dict()
        actual_port_obj_list = HWCloudHighRiskPort.objects.all()
        if len(actual_port_obj_list) != 0:
            logger.info("[scan_high_level_port] There has data, no initial data")
            return
        default_port_list = list(default_port_dict.keys())
        save_list_data = [HWCloudHighRiskPort(port=create_port, desc=default_port_dict[create_port]) for create_port in
                          default_port_list]
        with transaction.atomic():
            HWCloudHighRiskPort.objects.bulk_create(save_list_data)
        logger.info("----------------1.finish scan high level port-----------------")

    @classmethod
    def once_job(cls):
        cls.scan_high_level_port()
