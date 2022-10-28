# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 17:11
# @Author  : Tom_zc
# @FileName: permission_thread.py
# @Software: PyCharm
import logging
import time
import traceback
import requests
import base64
from django.db import transaction
from django.conf import settings
from open_infra.tools.scan_server_info import scan_server_info
from open_infra.utils.utils_kubeconfig import KubeconfigLib
from permission.models import KubeConfigInfo, ServiceInfo
from permission.resources.constants import PermissionGlobalConfig

logger = logging.getLogger("django")


class KubeconfigRefreshServiceInfoThread:
    @classmethod
    def push_service_txt(cls, content, token, timeout=60):
        """push service txt to github"""
        url = PermissionGlobalConfig.service_txt_url
        result = requests.get(url, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception("[refresh_service_txt] get url failed, code:{}, err:{}".format(result.status_code, result.content))
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
            raise Exception("[refresh_service_txt] put url failed, code:{}, err:{}".format(result.status_code, result.content))
        return result.content

    @classmethod
    def update_service(cls):
        """refresh service data from obs to mysql"""
        try:
            logger.info("------------------start to update service----------------------")
            dict_data = scan_server_info()
            with transaction.atomic():
                ServiceInfo.objects.all().delete()
                for service_name, server_info in dict_data.items():
                    ServiceInfo.objects.create(service_name=service_name,
                                               namespace=server_info["namespace"],
                                               cluster=server_info["cluster"],
                                               url=server_info["cluster_url"])
            service_obj_list = ServiceInfo.objects.all().values("service_name")
            service_name_list = [service_obj["service_name"] for service_obj in service_obj_list]
            content = "\n".join(service_name_list)
            cls.push_service_txt(content, settings.GITHUB_SECRET)
            logger.info("------------------end to update service----------------------")
        except Exception as e:
            logger.error("[update_service] e:{}, traceback:{}".format(e, traceback.format_exc()))

    @classmethod
    def immediately_cron_job(cls):
        cls.update_service()


class KubeconfigClearExpiredThread:
    @classmethod
    def clear_expired_data(cls):
        """Traverse all lists, determine the expiration time of all data, and delete expired data"""
        try:
            cur_time = int(time.time())
            config_list = KubeConfigInfo.objects.all()
            for config_info in config_list:
                try:
                    review_time = int(time.mktime(config_info.review_time.timetuple()))
                    expired_interval = int(config_info.expired_time) * 24 * 60 * 60
                    if cur_time >= review_time + expired_interval:
                        logger.info("[KubeconfigClearExpiredThread] start to delete expired data:{}, {}".format(
                            config_info.username, config_info.service_name))
                        service_info_list = ServiceInfo.objects.filter(service_name=config_info.service_name)
                        if len(service_info_list) == 0:
                            logger.error(
                                "[KubeconfigClearExpiredThread] get empty service info:{}".format(
                                    config_info.service_name))
                            continue
                        dict_data = dict()
                        dict_data["namespace"] = service_info_list[0].namespace
                        dict_data["cluster"] = service_info_list[0].cluster
                        dict_data["role"] = config_info.role
                        dict_data["username"] = config_info.username
                        KubeconfigLib.delete_kubeconfig(dict_data)
                        KubeConfigInfo.objects.filter(id=config_info.id).delete()
                except Exception as e:
                    logger.error("[KubeconfigClearExpiredThread] clear single data failed, e:{},traceback:{}".format(e,
                                                                                                                     traceback.format_exc()))
        except Exception as e:
            logger.error(
                "[KubeconfigClearExpiredThread] work thread fail:{}, traceback:{}".format(e, traceback.format_exc()))

    @classmethod
    def cron_job(cls):
        cls.clear_expired_data()
