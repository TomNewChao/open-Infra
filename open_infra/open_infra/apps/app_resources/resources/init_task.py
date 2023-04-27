# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 16:03
# @Author  : Tom_zc
# @FileName: init_task.py
# @Software: PyCharm
import datetime
import os
import time
import yaml
from django.conf import settings

from app_resources.models import HWCloudProjectInfo, HWCloudAccount, HWCloudEipInfo, ServiceInfo, \
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

    @classmethod
    @func_catch_exception
    def refresh_service(cls):
        """Read the information from uptime-robot and swr and deploy config, and refresh data to mysql"""
        logger.info("----------------3.start refresh service information-----------------")
        swr_info, config_list = CollectServiceInfo.get_all_service()
        client = CollectServiceInfo.get_swr_client()
        for config in config_list:
            service_info = ServiceInfo.create_single(service_name=config["service_name"],
                                                     namespace=config["namespace"],
                                                     cluster=config["cluster"],
                                                     region=config["region"])
            for image in config["image"]:
                image_name = image["image"].split(":")[0]
                image_info = swr_info.get(image_name, dict())
                new_dict = dict()
                new_dict["image"] = image_name
                new_dict["repository"] = image_info.get("repository")
                new_dict["branch"] = image_info.get("branch")
                new_dict["developer"] = image_info.get("developer")
                new_dict["email"] = image_info.get("email")
                new_dict["base_image"] = image_info.get("base_image")
                new_dict["base_os"] = image_info.get("os")
                new_dict["pipline_url"] = image_info.get("pipline_url")
                new_dict["num_download"] = image_info.get("num_download")
                if image_info.get("namespace") and image_info.get("name"):
                    swr_tag_info = CollectServiceInfo.get_swr_tag(image_info["namespace"], image_info["name"], client=client)
                    new_dict["size"] = swr_tag_info and (swr_tag_info.size >> 20) + 1
                    # to resolve the api of huaweicloud flow control
                    time.sleep(0.5)
                else:
                    new_dict["size"] = None
                new_dict["cpu_limit"] = image.get("cpu")
                new_dict["mem_limit"] = image.get("mem")
                new_dict["service"] = service_info
                ServiceImage.create_single(**new_dict)
        logger.info("----------------3.end to refresh service-----------------")

    @classmethod
    @func_catch_exception
    def refersh_service_sla(cls):
        logger.info("----------------4.start refresh service sla information-----------------")
        sla_mgr = SlaMgr()
        sla_list = sla_mgr.query_all_sla_info()
        path = os.path.join(settings.BASE_DIR, "config", "sla.yaml")
        with open(path, "r+", encoding="gbk") as file:
            list_data = yaml.load(file, Loader=yaml.FullLoader)
        service_sla_dict = {data["service_alias"]: data["service_introduce"] for data in list_data}
        # The service in sla but not in the table of service sla
        for sla_info in sla_list:
            if ServiceSla.get_by_url(url=sla_info["url"]) == 0:
                service_alias = sla_info.get('service_alias')
                save_dict = {
                    "url": sla_info["url"],
                    "service_introduce": service_sla_dict.get(service_alias),
                    "service_alias": service_alias,
                    "service_zone": sla_info.get('service_zone'),
                    "month_abnormal_time": sla_info.get('month_abnormal_time'),
                    "year_abnormal_time": sla_info.get('year_abnormal_time'),
                    "month_sla": sla_info.get('month_sla'),
                    "year_sla": sla_info.get('year_sla'),
                    "remain_time": sla_info.get('remain_time'),
                }
                ServiceSla.create_single(**save_dict)
            else:
                update_dict = {
                    "month_abnormal_time": sla_info.get('month_abnormal_time'),
                    "year_abnormal_time": sla_info.get('year_abnormal_time'),
                    "month_sla": sla_info.get('month_sla'),
                    "year_sla": sla_info.get('year_sla'),
                    "remain_time": sla_info.get('remain_time'),
                }
                ServiceSla.update_url(sla_info, **update_dict)
        # delete url
        # The service in service sla but not in the sla
        sla_url_list = [sla_info["url"] for sla_info in sla_list]
        service_sla_url_list = [service_sla["url"] for service_sla in ServiceSla.get_all_url()]
        not_exist_url = list(set(sla_url_list) - set(service_sla_url_list))
        logger.info("refresh sla service:{}.".format(",".join(not_exist_url)))
        ServiceSla.delete_by_url(not_exist_url)
        logger.info("----------------4.end to refresh sla service-----------------")

    @classmethod
    @func_catch_exception
    def refresh_service_swr(cls):
        """refresh service swr"""
        logger.info("----------------5.start refresh service swr information-----------------")
        swr_info = CollectServiceInfo.get_swr_data()
        image_list = ServiceImage.get_all_image()
        client = CollectServiceInfo.get_swr_client()
        for image in image_list:
            image_info = swr_info.get(image['image'])
            if image_info:
                new_dict = dict()
                new_dict["repository"] = image_info.get("repository")
                new_dict["branch"] = image_info.get("branch")
                new_dict["developer"] = image_info.get("developer")
                new_dict["email"] = image_info.get("email")
                new_dict["base_image"] = image_info.get("base_image")
                new_dict["base_os"] = image_info.get("os")
                new_dict["pipline_url"] = image_info.get("pipline_url")
                new_dict["num_download"] = image_info.get("num_download")
                if image_info.get("namespace") and image_info.get("name"):
                    swr_tag_info = CollectServiceInfo.get_swr_tag(image_info["namespace"], image_info["name"], client=client)
                    new_dict["size"] = swr_tag_info and (swr_tag_info.size >> 20) + 1
                    # to resolve the api of huaweicloud flow control
                    time.sleep(0.5)
                else:
                    new_dict["size"] = None
                ServiceImage.update_images(image['image'], **new_dict)
        logger.info("----------------5.end refresh service swr information-----------------")

    @classmethod
    def crontab_task(cls):
        cls.refresh_account_info()
        cls.refresh_eip()
        cls.refersh_service_sla()
        cls.refresh_service_swr()

    @classmethod
    def immediately_task(cls):
        pass

    @classmethod
    def test_task(cls):
        # cls.refresh_account_info()
        # cls.refresh_eip()
        # cls.refresh_sla_config()
        # ServiceImage.delete_all()
        # ServiceSla.delete_all()
        # ServiceInfo.delete_all()
        # cls.refresh_service()
        cls.refersh_service_sla()
