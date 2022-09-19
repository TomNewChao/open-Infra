# -*- coding: utf-8 -*-
# @Time    : 2022/9/19 14:12
# @Author  : Tom_zc
# @FileName: alarm_handler.py
# @Software: PyCharm
import json
import math
import traceback
import requests
import logging

from alarm.resources.alarm_module.constants import AlarmType

logger = logging.getLogger("django")


class AlarmHandlerConfig(object):
    container_cpu_query = "{}/api/v1/query?query=sum(rate(container_cpu_usage_seconds_total[5m])) by (pod, container,namespace,cluster, account,name) / sum(container_spec_cpu_quota/container_spec_cpu_period) by (pod, container,namespace,cluster, account, name)&time={}"
    container_mem_query = "{}/api/v1/query?query=sum(container_memory_working_set_bytes) by (pod, container,namespace,cluster, account,name) / sum(container_spec_memory_limit_bytes) by (pod, container,namespace,cluster, account,name) * 100 != +inf&time={}"
    container_fs_query = "{}/api/v1/query?query=sum(container_fs_usage_bytes) by(pod, container,namespace,cluster, account,name) / sum(container_fs_limit_bytes) by(pod, container,namespace,cluster, account,name) * 100 != +inf&time={}"
    node_cpu_query = "{}/api/v1/query?query=node_cpu_seconds_total&time={}"
    node_mem_query = "{}/api/v1/query?query=node_memory_MemUsed&time={}"
    node_fs_query = "{}/api/v1/query?query=sum(node_filesystem_free_bytes) by(node_name, job) / sum(node_filesystem_size_bytes) by(node_name, job) * 100 != +inf&time={}"
    pass


class AlarmBaseHandler(object):

    @classmethod
    def get_metrics_data(cls, url):
        data = requests.get(url, timeout=(60, 60))
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
            alarm_list_data = list()
            list_data = cls.get_metrics_data(query)
            for metrics_dict in list_data:
                if metrics_dict["value"][1] in ["-Inf", "NaN", "+Inf"]:
                    continue
                value = round(float(metrics_dict["value"][1]))
                abs_value = math.fabs(value)
                if abs_value > 100.0:
                    continue
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
                name = "{}/{}/{}/{}/{}".format(metrics_dict["metric"]["account"],
                                               metrics_dict["metric"]["cluster"],
                                               metrics_dict["metric"]["namespace"],
                                               metrics_dict["metric"]["pod"],
                                               metrics_dict["metric"]["name"])
                if abs_value >= alarm_threshold:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.ALARM,
                        "report_retry_count": 2,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                else:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.RECOVER,
                        "report_retry_count": 2,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                alarm_list_data.append(alarm_info_dict)
            return alarm_list_data
        except Exception as e:
            logger.error("[get_container_alarm_info] e:{}, traceback:{}".format(e, traceback.format_exc()))
            return list()

    @classmethod
    def get_node_alarm_info(cls, query, alarm_threshold, alarm_code):
        try:
            alarm_list_data = list()
            list_data = cls.get_metrics_data(query)
            for metrics_dict in list_data:
                if metrics_dict["value"][1] in ["-Inf", "NaN", "+Inf"]:
                    continue
                value = round(float(metrics_dict["value"][1]))
                abs_value = math.fabs(value)
                if abs_value > 100.0:
                    continue
                elif metrics_dict["metric"].get("job") is None:
                    continue
                elif metrics_dict["metric"].get("node_name") is None:
                    continue
                name = "{}/{}".format(metrics_dict["metric"]["job"],
                                      metrics_dict["metric"]["node_name"])
                if abs_value >= alarm_threshold:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.ALARM,
                        "report_retry_count": 2,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                else:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.RECOVER,
                        "report_retry_count": 2,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                alarm_list_data.append(alarm_info_dict)
            return alarm_list_data
        except Exception as e:
            logger.error("[get_node_alarm_info] e:{}, traceback:{}".format(e, traceback.format_exc()))
            return list()

    @classmethod
    def get_node_fs_alarm_info(cls, query, alarm_threshold, alarm_code):
        try:
            alarm_list_data = list()
            list_data = cls.get_metrics_data(query)
            for metrics_dict in list_data:
                if metrics_dict["value"][1] == "NaN":
                    continue
                value = round(float(metrics_dict["value"][1]))
                abs_value = math.fabs(value)
                abs_value = 1.0 - abs_value
                if abs_value > 100.0:
                    continue
                elif metrics_dict["metric"].get("job") is None:
                    continue
                elif metrics_dict["metric"].get("node_name") is None:
                    continue
                name = "{}/{}".format(metrics_dict["metric"]["job"],
                                      metrics_dict["metric"]["node_name"])
                if abs_value >= alarm_threshold:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.ALARM,
                        "report_retry_count": 2,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                else:
                    alarm_info_dict = {
                        "alarm_type": AlarmType.RECOVER,
                        "report_retry_count": 2,
                        "alarm_info_dict": {
                            "alarm_id": alarm_code,
                            "des_var": [name, "{}%".format(alarm_threshold)],
                        }
                    }
                alarm_list_data.append(alarm_info_dict)
            return alarm_list_data
        except Exception as e:
            logger.error("[get_node_alarm_info] e:{}, traceback:{}".format(e, traceback.format_exc()))
            return list()
