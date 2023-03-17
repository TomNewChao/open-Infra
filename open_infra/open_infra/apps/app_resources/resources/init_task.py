# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 16:03
# @Author  : Tom_zc
# @FileName: init_task.py
# @Software: PyCharm
import datetime
import os
from urllib.parse import urlparse

import yaml
from django.conf import settings

from app_resources.models import HWCloudProjectInfo, HWCloudAccount, HWCloudEipInfo, ServiceSlaConfig, ServiceInfo, \
    ServiceSla, ServiceImage
from app_resources.resources.account_mgr import AccountMgr
from app_resources.resources.sla_mgr import SlaMgr
from open_infra.tools.scan_image import CollectServiceInfo
from open_infra.utils.common import func_retry, func_catch_exception
from open_infra.tools.scan_eip import scan_eip
from django.db import transaction
from logging import getLogger

logger = getLogger("django")


class InitMgr:
    @classmethod
    @func_retry()
    def refresh_account_info(cls):
        """query HWCloud account information: include zone and project id, refresh to database"""
        logger.info("----------------1.start query_account_info-----------------------")
        account_info_list = AccountMgr.get_hw_account_project_info_from_obs()
        with transaction.atomic():
            # 1.delete data
            HWCloudProjectInfo.delete_all()
            HWCloudAccount.delete_all()
            # 2.save data
            for account_info in account_info_list:
                account = account_info["account"]
                ak = account_info["ak"]
                sk = account_info["sk"]
                account_obj = HWCloudAccount.create_single(account=account, ak=ak, sk=sk)
                for project_info in account_info["project_info"]:
                    project_id = project_info["project_id"]
                    zone = project_info["zone"]
                    HWCloudProjectInfo.create_single(id=project_id, zone=zone, account=account_obj)
            # 3.clean memcached
            AccountMgr.account_info_list = list()
        logger.info("----------------1.finish query_account_info-----------------------")

    @classmethod
    @func_catch_exception
    def refresh_eip(cls):
        logger.info("----------------2.start scan_eip-----------------------")
        account_info = AccountMgr.get_decrypt_hw_account_project_info_from_database()
        eip_dict = scan_eip(account_info)
        with transaction.atomic():
            HWCloudEipInfo.delete_all()
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
                    HWCloudEipInfo.create_single(**dict_data)
        logger.info("----------------2.finish scan_eip-----------------------")

    @staticmethod
    @func_retry()
    def refresh_sla_config():
        """Through to reading the default high level port from config and write to mysql """
        logger.info("----------------3.start refresh sla config-----------------")
        service_sla_config = ServiceSlaConfig.all()
        if len(service_sla_config) != 0:
            logger.info("[refresh_sla_config] The data is existed, no initial data")
        else:
            path = os.path.join(settings.BASE_DIR, "config", "sla.yaml")
            with open(path, "r+", encoding="gbk") as file:
                list_data = yaml.load(file, Loader=yaml.FullLoader)
            save_list_data = [ServiceSlaConfig(url=data["url"], service_alias=data["service_alias"],
                                               service_introduce=data["service_introduce"]) for data in list_data]
            ServiceSlaConfig.create_all(save_list_data)
        logger.info("----------------3.finish refresh sla config-----------------")

    @classmethod
    @func_catch_exception
    def refresh_service(cls):
        """Read the information from uptime-robot and swr and deploy config, and refresh data to mysql"""
        logger.info("----------------4.start refresh service information-----------------")
        swr_info, config_list = CollectServiceInfo.get_service()
        sla_mgr = SlaMgr()
        sla_dict = sla_mgr.query_all_sla_info()
        ServiceImage.delete_all()
        ServiceSla.delete_all()
        ServiceInfo.delete_all()
        for config in config_list:
            # todo how to refresh data, need to option, now use first to delete and second to add, ok, it is madness
            service_info = ServiceInfo.create_single(service_name=config["service_name"],
                                                     namespace=config["namespace"],
                                                     cluster=config["cluster"],
                                                     region=config["region"])
            for image in config["image"]:
                image_name = image["image"].split(":")[0]
                image_info = swr_info.get(image_name)
                if image_info:
                    new_dict = dict()
                    new_dict["image"] = image_info.get("path")
                    new_dict["repository"] = image_info.get("repository")
                    new_dict["branch"] = image_info.get("branch")
                    new_dict["developer"] = image_info.get("developer")
                    new_dict["email"] = image_info.get("email")
                    new_dict["base_image"] = image_info.get("base_image")
                    new_dict["base_os"] = image_info.get("os")
                    new_dict["pipline_url"] = image_info.get("pipline_url")
                    new_dict["num_download"] = image_info.get("num_download")
                    new_dict["size"] = image_info.get("size")
                    new_dict["cpu_limit"] = image.get("cpu")
                    new_dict["mem_limit"] = image.get("mem")
                    new_dict["service"] = service_info
                    ServiceImage.objects.create(**new_dict)
                else:
                    logger.error("[refresh_service] There find not exist image:{}".format(image_name))
            for url in config["url"]:
                if url.startswith(r"http"):
                    url = urlparse(url).netloc
                sla_info = sla_dict.get(url)
                if sla_info is None:
                    continue
                if ServiceSla.objects.filter(url=sla_info["url"]).count() > 0:
                    continue
                sla_config = ServiceSlaConfig.objects.filter(url=sla_info["url"])
                if len(sla_config):
                    service_alias = sla_config[0]["service_alias"]
                    service_introduce = sla_config[0]["service_introduce"]
                else:
                    service_alias = ""
                    service_introduce = ""
                save_dict = {
                    "url": sla_info["url"],
                    "service_alias": service_alias,
                    "service_introduce": service_introduce,
                    "service_zone": sla_info.get('service_zone'),
                    "month_abnormal_time": sla_info.get('month_abnormal_time'),
                    "year_abnormal_time": sla_info.get('year_abnormal_time'),
                    "month_sla": sla_info.get('month_sla'),
                    "year_sla": sla_info.get('year_sla'),
                    "remain_time": sla_info.get('remain_time'),
                    "service": service_info,
                }
                ServiceSla.create_single(**save_dict)
        logger.info("----------------4.end to refresh service-----------------")

    @classmethod
    def crontab_task(cls):
        cls.refresh_account_info()
        cls.refresh_eip()
        cls.refresh_service()

    @classmethod
    def immediately_task(cls):
        cls.refresh_sla_config()

    @classmethod
    def test_task(cls):
        # cls.refresh_account_info()
        # cls.refresh_eip()
        # cls.refresh_sla_config()
        cls.refresh_service()
