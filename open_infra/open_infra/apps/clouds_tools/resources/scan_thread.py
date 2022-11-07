# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 11:27
# @Author  : Tom_zc
# @FileName: scan_thread.py
# @Software: PyCharm
import base64
import datetime
import time
import traceback
import django.db
import requests
from django.conf import settings

from clouds_tools.models import HWCloudAccount, HWCloudProjectInfo, HWCloudEipInfo, HWCloudScanEipPortInfo, \
    HWCloudScanEipPortStatus, HWCloudScanObsAnonymousStatus, HWCloudScanObsAnonymousBucket, HWCloudScanObsAnonymousFile, \
    HWCloudHighRiskPort, ServiceInfo
from clouds_tools.resources.constants import ScanToolsLock, ClousToolsGlobalConfig
from clouds_tools.resources.scan_tools import ScanBaseTools, ScanOrmTools, SlaMgr
from open_infra.tools.scan_server_info import scan_server_info
from open_infra.utils.common import func_retry, func_catch_exception
from open_infra.utils.default_port_list import HighRiskPort
from open_infra.tools.scan_eip import scan_eip
from open_infra.tools.scan_port import scan_port
from open_infra.tools.scan_obs import scan_obs
from logging import getLogger
from django.db import transaction

logger = getLogger("django")


class ScanToolsOnceJobThread(object):

    @classmethod
    @func_retry()
    def scan_high_level_port(cls):
        logger.info("----------------1.start scan high level port-----------------")
        default_port_dict = HighRiskPort.get_port_dict()
        actual_port_obj_list = HWCloudHighRiskPort.objects.all()
        if len(actual_port_obj_list) != 0:
            logger.info("[scan_high_level_port] There has data, no initial data")
        else:
            default_port_list = list(default_port_dict.keys())
            save_list_data = [HWCloudHighRiskPort(port=create_port, desc=default_port_dict[create_port]) for create_port in
                              default_port_list]
            with transaction.atomic():
                HWCloudHighRiskPort.objects.bulk_create(save_list_data)
        logger.info("----------------1.finish scan high level port-----------------")

    @classmethod
    def once_job(cls):
        cls.scan_high_level_port()


class ScanToolsCronJobRefreshDataThread(object):
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
    @func_catch_exception
    def scan_eip(cls):
        logger.info("----------------2.start scan_eip-----------------------")
        account_info = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        eip_dict = scan_eip(account_info)
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
    def push_service_txt(cls, content, token, timeout=60):
        """push service txt to github"""
        url = ClousToolsGlobalConfig.service_txt_url
        result = requests.get(url, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception(
                "[refresh_service_txt] get url failed, code:{}, err:{}".format(result.status_code, result.content))
        sha = result.json()["sha"]
        base64_content = str(base64.b64encode(content.encode("utf-8")), 'utf-8')
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer {}".format(token)
        }
        json_data = {
            "message": "refresh service info {}".format(int(time.time())),
            "committer": settings.GITHUB_COMMIT_INFO,
            "sha": sha,
            "content": base64_content
        }
        result = requests.put(url=url, headers=headers, json=json_data, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception(
                "[refresh_service_txt] put url failed, code:{}, err:{}".format(result.status_code, result.content))
        return result.content

    @classmethod
    @func_catch_exception
    def update_service(cls):
        """refresh service data from obs to mysql"""
        logger.info("------------------4.start to update service----------------------")
        dict_data = scan_server_info()
        sla_mgr = SlaMgr()
        sla_info_list = sla_mgr.query_all_sla_info()
        with transaction.atomic(), ScanToolsLock.refresh_service_info_lock:
            ServiceInfo.objects.all().delete()
            for service_name, server_info in dict_data.items():
                ServiceInfo.objects.create(service_name=service_name,
                                           namespace=server_info["namespace"],
                                           cluster=server_info["cluster"],
                                           url=server_info["cluster_url"])
            for sla_info in sla_info_list:
                service_name = sla_info.get("name")
                if service_name:
                    ServiceInfo.objects.filter(service_name=service_name).update(
                        service_alias=sla_info["name-alias"],
                        url_alias=sla_info["sla_url"],
                        service_introduce=sla_info["introduce"],
                        community=sla_info["sla_zone"],
                        month_abnormal_time=float(sla_info["month_exp_min"]),
                        year_abnormal_time=float(sla_info["year_exp_min"]),
                        month_sla=float(sla_info["month_sla"]),
                        year_sla=float(sla_info["year_sla"]),
                        remain_time=float(sla_info["sla_year_remain"]),
                    )
                else:
                    ServiceInfo.objects.create(service_name=service_name,
                                               service_alias=sla_info["name-alias"],
                                               url_alias=sla_info["sla_url"],
                                               service_introduce=sla_info["introduce"],
                                               community=sla_info["sla_zone"],
                                               month_abnormal_time=float(sla_info["month_exp_min"]),
                                               year_abnormal_time=float(sla_info["year_exp_min"]),
                                               month_sla=float(sla_info["month_sla"]),
                                               year_sla=float(sla_info["year_sla"]),
                                               remain_time=float(sla_info["sla_year_remain"]))
        service_obj_list = ServiceInfo.objects.all().values("service_name")
        service_name_list = [service_obj["service_name"] for service_obj in service_obj_list if service_obj["service_name"]]
        content = "\n".join(service_name_list)
        cls.push_service_txt(content, settings.GITHUB_SECRET)
        logger.info("------------------4.end to update service----------------------")

    @classmethod
    def immediately_cron_job(cls):
        cls.query_account_info()
        cls.scan_eip()
        cls.scan_sla()
        cls.update_service()


class ScanToolsCronJobScanThread(object):
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
    def cron_job(cls):
        try:
            ScanToolsLock.scan_port.acquire()
            cls.scan_port()
        except Exception as e:
            logger.error("[cron_job] e:{}, traceback:{}".format(e, traceback.format_exc()))
        finally:
            ScanToolsLock.scan_port.release()
        try:
            ScanToolsLock.scan_obs.acquire()
            cls.scan_obs()
        except Exception as e:
            logger.error("[cron_job] e:{}, traceback:{}".format(e, traceback.format_exc()))
        finally:
            ScanToolsLock.scan_obs.release()


class ScanToolsIntervalJobScanThread(object):
    @classmethod
    @func_catch_exception
    def refresh_sla(cls):
        sla_mgr = SlaMgr()
        django.db.close_old_connections()
        sla_info_list = sla_mgr.query_all_sla_info()
        with ScanToolsLock.refresh_service_info_lock:
            for sla_info in sla_info_list:
                service_name = sla_info.get("name")
                if service_name:
                    ServiceInfo.objects.filter(service_name=service_name).update(
                        month_abnormal_time=float(sla_info["month_exp_min"]),
                        year_abnormal_time=float(sla_info["year_exp_min"]),
                        month_sla=float(sla_info["month_sla"]),
                        year_sla=float(sla_info["year_sla"]),
                        remain_time=float(sla_info["sla_year_remain"]),
                    )

    @classmethod
    def interval_job(cls):
        cls.refresh_sla()
