# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 17:11
# @Author  : Tom_zc
# @FileName: permission_thread.py
# @Software: PyCharm
import logging
import time
import traceback

from app_resources.models import ServiceInfo
from open_infra.utils.utils_kubeconfig import KubeconfigLib
from permission.models import KubeConfigInfo

logger = logging.getLogger("django")


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
