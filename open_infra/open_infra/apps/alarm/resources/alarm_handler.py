# -*- coding: utf-8 -*-
# @Time    : 2022/9/19 14:12
# @Author  : Tom_zc
# @FileName: alarm_handler.py
# @Software: PyCharm
import math
import traceback
import requests
import logging

from collections import defaultdict
from alarm.resources.alarm_module.alarm_thread import AlarmTools
from alarm.resources.alarm_module.constants import AlarmType

logger = logging.getLogger("django")


class AlarmHandlerConfig(object):
    container_cpu_query = "{}/api/v1/query?query=container_cpu_usage_rate&time={}"
    container_mem_query = "{}/api/v1/query?query=container_mem_usage_rate&time={}"
    container_fs_query = "{}/api/v1/query?query=container_fs_usage_rate&time={}"
    container_res_count_query = "{}/api/v1/query?query=container_cpu_usage_seconds_total&time={}"
    node_cpu_query = "{}/api/v1/query?query=node_cpu_seconds_total&time={}"
    node_mem_query = "{}/api/v1/query?query=node_memory_MemUsed&time={}"
    node_fs_query = "{}/api/v1/query?query=node_filesystem_usage_rate&time={}"


class AlarmBaseHandler(object):

    @classmethod
    def get_metrics_data(cls, url):
        data = requests.get(url, timeout=(300, 300))
        if data.status_code != 200:
            logger.info("[get_metrics_data] get metrics data failed:{}".format(data.status_code))
            return list()
        list_dict = data.json()
        if not isinstance(list_dict, dict) or list_dict.get("data") is None:
            logger.info("[get_metrics_data] get metrics invalid data ")
            return list()
        return list_dict["data"]["result"]

    @classmethod
    def get_container_alarm_info(cls, query, alarm_threshold, alarm_code):
        try:
            alarm_list_data, alarm_md5_data = list(), list()
            list_data = cls.get_metrics_data(query)
            for metrics_dict in list_data:
                if metrics_dict["value"][1] in ["-Inf", "NaN", "+Inf"]:
                    continue
                value = round(float(metrics_dict["value"][1]))
                abs_value = math.fabs(value)
                if metrics_dict["metric"].get("account") is None:
                    continue
                elif metrics_dict["metric"].get("cluster") is None:
                    continue
                elif metrics_dict["metric"].get("namespace") is None:
                    continue
                elif metrics_dict["metric"].get("pod") is None:
                    continue
                elif metrics_dict["metric"].get("name") is None:
                    continue
                elif metrics_dict["metric"]["cluster"] == "openeuler-cn-north4-x86-cluster" and metrics_dict["metric"]["namespace"] == "jenkins":
                    pod_name = metrics_dict["metric"]["pod"]
                    if pod_name.startswith("k8s-x86-oe") or pod_name.startswith("k8s-x86-openeuler") or pod_name.startswith("k8s-x86-rtos-openeuler-test") or pod_name.startswith("k8s-x86-soe"):
                        continue
                elif metrics_dict["metric"]["cluster"] in ["openeuler-arm-jenkins-cluster", "openeuler-cn-north4-arm-cluster"] and metrics_dict["metric"]["namespace"] == "jenkins":
                    continue
                elif metrics_dict["metric"]["cluster"] == "mindspore-cn-north-4-arm-new-cluster" and metrics_dict["metric"]["namespace"] == "jenkins" and metrics_dict["metric"]["pod"].startswith("arm-centos-slaves"):
                    continue
                elif metrics_dict["metric"]["cluster"] == "openlookeng-tryme-cluster" and metrics_dict["metric"]["namespace"].startswith(r"lk-"):
                    continue
                name = "{}/{}/{}/{}/{}".format(metrics_dict["metric"]["account"],
                                               metrics_dict["metric"]["cluster"],
                                               metrics_dict["metric"]["namespace"],
                                               metrics_dict["metric"]["pod"],
                                               metrics_dict["metric"]["name"])
                if abs_value >= alarm_threshold:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.ALARM,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                else:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.RECOVER,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                alarm_md5 = AlarmTools.gen_alarm_md5(alarm_info_dict["alarm_info_dict"])
                alarm_md5_data.append(alarm_md5)
                alarm_list_data.append(alarm_info_dict)
            return alarm_list_data, alarm_md5_data
        except Exception as e:
            logger.error("[get_container_alarm_info] e:{}, traceback:{}".format(e, traceback.format_exc()))
            return list(), list()

    @classmethod
    def get_node_alarm_info(cls, query, alarm_threshold, alarm_code):
        try:
            alarm_list_data, alarm_md5_data = list(), list()
            list_data = cls.get_metrics_data(query)
            for metrics_dict in list_data:
                if metrics_dict["value"][1] in ["-Inf", "NaN", "+Inf"]:
                    continue
                value = round(float(metrics_dict["value"][1]))
                abs_value = math.fabs(value)
                if metrics_dict["metric"].get("job") is None:
                    continue
                elif metrics_dict["metric"].get("node_name") is None:
                    continue
                name = "{}/{}".format(metrics_dict["metric"]["job"],
                                      metrics_dict["metric"]["node_name"])
                if abs_value >= alarm_threshold:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.ALARM,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                else:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.RECOVER,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                alarm_md5 = AlarmTools.gen_alarm_md5(alarm_info_dict["alarm_info_dict"])
                alarm_md5_data.append(alarm_md5)
                alarm_list_data.append(alarm_info_dict)
            return alarm_list_data, alarm_md5_data
        except Exception as e:
            logger.error("[get_node_alarm_info] e:{}, traceback:{}".format(e, traceback.format_exc()))
            return list(), list()

    @classmethod
    def get_container_count_info(cls, query, alarm_threshold, alarm_code):
        try:
            count_server_count = defaultdict(int)
            alarm_list_data = list()
            list_data = cls.get_metrics_data(query)
            for metrics_dict in list_data:
                account = metrics_dict["metric"].get("account")
                cluster = metrics_dict["metric"].get("cluster")
                namespace = metrics_dict["metric"].get("namespace")
                pod = metrics_dict["metric"].get("pod")
                if not (account and cluster and pod and namespace):
                    logger.info("[get_container_count_info] get fault data:{},{},{},{}".format(account, cluster, namespace, pod))
                if pod.startswith("res"):
                    key = "{}/{}/{}".format(account, cluster, namespace)
                    count_server_count[key] += 1
            for name, value in count_server_count.items():
                alarm_threshold_number = alarm_threshold.get(name, 100)
                if value/2 >= alarm_threshold_number:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.ALARM,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}".format(alarm_threshold_number)],
                        }
                    }
                else:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.RECOVER,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}".format(alarm_threshold_number)],
                        }
                    }
                alarm_list_data.append(alarm_info_dict)
            return alarm_list_data
        except Exception as e:
            logger.error("[get_container_count_info] e:{}, traceback:{}".format(e, traceback.format_exc()))
            return list()
