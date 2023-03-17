# -*- coding: utf-8 -*-
# @Time    : 2023/1/9 10:30
# @Author  : Tom_zc
# @FileName: resource_utilization_mgr.py
# @Software: PyCharm
import time
import traceback

import requests
import logging
import datetime

from collections import defaultdict
from django.conf import settings
from django.db import models

from consumption_control.models import CpuResourceUtilization, MemResourceUtilization
from consumption_control.resources.alarm import ResourceUtilizationAlarm
from consumption_control.resources.constants import AlarmHandlerRangeConfig
from open_infra.utils.common import output_table_excel

logger = logging.getLogger("django")


class ResourceUtilizationInitialMgr:
    def __init__(self):
        super(ResourceUtilizationInitialMgr, self).__init__()

    def get_start_time(self):
        date_now = datetime.datetime.now()
        date_format = "{}-{}-{} 00:00:00"
        cur_date = date_format.format(date_now.year, date_now.month, date_now.day)
        time_array = time.strptime(cur_date, "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(time_array))

    def get_range_data(self, prom_query=AlarmHandlerRangeConfig.node_cpu_query, cur_time=None):
        try:
            if cur_time is None:
                cur_time = time.time()
            start = cur_time - AlarmHandlerRangeConfig.RANGE_TIME
            url = prom_query.format(AlarmHandlerRangeConfig.ALARM_PROMETHEUS_URL, start,
                                    cur_time, AlarmHandlerRangeConfig.STEP)
            data = requests.get(url, timeout=(1200, 1200))
            if not str(data.status_code).startswith("20"):
                raise Exception("get status code:{}".format(data.status_code))
            return data.json()["data"]["result"]
        except Exception as e:
            logger.error("[get_range_data] {}, traceback:{}".format(e, traceback.format_exc()))
            return []

    def parse_data(self, prom_data_list):
        dict_data = defaultdict(list)
        for prom_data in prom_data_list:
            key = prom_data["metric"]["node_name"]
            for pro_value in prom_data["values"]:
                value = round(float(pro_value[1]), 2)
                dict_data[key].append(value)
        return dict_data

    def resouce_utilization(self):
        logger.info("-------------------start to resouce_utilization---------------")
        start_time = int(time.time())
        cur_time = self.get_start_time()
        cpu_data = self.get_range_data(cur_time=cur_time)
        mem_data = self.get_range_data(AlarmHandlerRangeConfig.node_mem_query, cur_time=cur_time)
        if not cpu_data or not mem_data:
            raise Exception("[resouce_utilization] get data failed")
        cpu_dict = self.parse_data(cpu_data)
        mem_dict = self.parse_data(mem_data)
        cpu_threshold = settings.RESOURCE_UTILIZATION_CPU_THRESHOLD
        mem_threshold = settings.RESOURCE_UTILIZATION_MEM_THRESHOLD
        # 1.first to delete data
        expire_timestamps = int(cur_time) - AlarmHandlerRangeConfig.EXPIRED_DAY
        CpuResourceUtilization.delete_con(expire_timestamps)
        MemResourceUtilization.delete_con(expire_timestamps)
        for name, value_list in cpu_dict.items():
            if mem_dict.get(name) is None:
                logger.info("[resouce_utilization] prom exist in cpu and not in mem:{}".format(name))
                continue
            cpu_value_list = value_list
            mem_value_list = mem_dict[name]
            max_cpu_value = max(cpu_value_list)
            max_mem_value = max(mem_value_list)
            if max_cpu_value < cpu_threshold and max_mem_value < mem_threshold:
                # active alarm
                ResourceUtilizationAlarm.active_alarm(name)
                pass
            else:
                # recover alarm
                ResourceUtilizationAlarm.recover_alarm(name)
                pass
            lower_cpu_count = len(list(filter(lambda x: float(x) < 10.0, cpu_value_list)))
            medium_lower_cpu_count = len(list(filter(lambda x: 10.0 <= float(x) < 50.0, cpu_value_list)))
            medium_high_cpu_count = len(list(filter(lambda x: 50.0 <= float(x) < 90.0, cpu_value_list)))
            high_cpu_count = len(list(filter(lambda x: 90.0 <= float(x), cpu_value_list)))
            params = {
                "name": name,
                "lower_cpu_count": lower_cpu_count,
                "medium_lower_cpu_count": medium_lower_cpu_count,
                "medium_high_cpu_count": medium_high_cpu_count,
                "high_cpu_count": high_cpu_count,
                "create_time": int(cur_time),
            }
            CpuResourceUtilization.create_single(**params)
            lower_mem_count = len(list(filter(lambda x: float(x) < 10.0, mem_value_list)))
            medium_lower_mem_count = len(list(filter(lambda x: 10.0 <= float(x) < 50.0, mem_value_list)))
            medium_high_mem_count = len(list(filter(lambda x: 50.0 <= float(x) < 90.0, mem_value_list)))
            high_mem_count = len(list(filter(lambda x: 90.0 <= float(x), mem_value_list)))
            params = {
                "name": name,
                "lower_mem_count": lower_mem_count,
                "medium_lower_mem_count": medium_lower_mem_count,
                "medium_high_mem_count": medium_high_mem_count,
                "high_mem_count": high_mem_count,
                "create_time": int(cur_time),
            }
            MemResourceUtilization.create_single(**params)
        unexcept_name_list = list(set(mem_dict.keys()) - set(cpu_dict.keys()))
        for name in unexcept_name_list:
            logger.info("[resouce_utilization] prom exist in mem and not in cpu:{}".format(name))
        logger.info("-------------------resouce_utilization:spend time:{}-----------------".format(
            int(time.time()) - start_time))


class ResourceUtilizationMgr:
    def __init__(self):
        super(ResourceUtilizationMgr, self).__init__()

    def get_month(self, model):
        if not issubclass(model, models.Model):
            raise Exception("[get_month] model must be the sub class of models.Model")
        all_list = model.objects.order_by("-create_time").values("create_time").distinct()
        ret_list = list()
        for temp in all_list:
            dict_data = dict()
            time_array = time.localtime(temp["create_time"])
            date_temp = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            dict_data["title"] = date_temp
            dict_data["key"] = date_temp
            ret_list.append(dict_data)
        return ret_list

    def get_cpu_month(self):
        return self.get_month(CpuResourceUtilization)

    def get_mem_month(self):
        return self.get_month(MemResourceUtilization)

    def get_data(self, model, date_str):
        if not issubclass(model, models.Model):
            raise Exception("[get_data] model must be the sub class of models.Model")
        time_array = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        time_stamp = int(time.mktime(time_array))
        result_list = model.objects.filter(create_time=time_stamp)
        return result_list

    def get_cpu_data(self, date_str):
        result_list = self.get_data(CpuResourceUtilization, date_str)
        ret_list = list()
        for result in result_list:
            total_count = sum([result.lower_cpu_count, result.medium_lower_cpu_count,
                               result.medium_high_cpu_count, result.high_cpu_count])
            if result.lower_cpu_count > 0:
                ret_list.append([round((result.lower_cpu_count * 100.0) / total_count, 2), 0, result.name])
            if result.medium_lower_cpu_count > 0:
                ret_list.append([round((result.medium_lower_cpu_count * 100.0) / total_count, 2), 10, result.name])
            if result.medium_high_cpu_count > 0:
                ret_list.append([round((result.medium_high_cpu_count * 100.0) / total_count, 2), 50, result.name])
            if result.high_cpu_count > 0:
                ret_list.append([round((result.high_cpu_count * 100.0) / total_count, 2), 90, result.name])
        return ret_list

    def get_mem_data(self, date_str):
        result_list = self.get_data(MemResourceUtilization, date_str)
        ret_list = list()
        for result in result_list:
            total_count = sum([result.lower_mem_count, result.medium_lower_mem_count,
                               result.medium_high_mem_count, result.high_mem_count])
            if result.lower_mem_count > 0:
                ret_list.append([round((result.lower_mem_count * 100.0) / total_count, 2), 0, result.name])
            if result.medium_lower_mem_count > 0:
                ret_list.append([round((result.medium_lower_mem_count * 100.0) / total_count, 2), 10, result.name])
            if result.medium_high_mem_count > 0:
                ret_list.append([round((result.medium_high_mem_count * 100.0) / total_count, 2), 50, result.name])
            if result.high_mem_count > 0:
                ret_list.append([round((result.high_mem_count * 100.0) / total_count, 2), 90, result.name])
        return ret_list

    def get_cpu_table_data(self, date):
        result_list = self.get_data(CpuResourceUtilization, date)
        ret_list = list()
        for result in result_list:
            line_data = list()
            total_count = sum([result.lower_cpu_count, result.medium_lower_cpu_count,
                               result.medium_high_cpu_count, result.high_cpu_count])
            line_data.append(result.name)
            line_data.append(round((result.lower_cpu_count * 100.0) / total_count, 2))
            line_data.append(round((result.medium_lower_cpu_count * 100.0) / total_count, 2))
            line_data.append(round((result.medium_high_cpu_count * 100.0) / total_count, 2))
            line_data.append(round((result.high_cpu_count * 100.0) / total_count, 2))
            ret_list.append(line_data)
        title_name = ["服务器名称", "10>CPU资源利用率", "50>CPU资源利用率>=10", "90>CPU资源利用率>=50", "CPU资源利用率>=90"]
        return output_table_excel("cpu", title_name, ret_list)

    def get_mem_table_data(self, date):
        result_list = self.get_data(MemResourceUtilization, date)
        ret_list = list()
        for result in result_list:
            line_data = list()
            line_data.append(result.name)
            total_count = sum([result.lower_mem_count, result.medium_lower_mem_count,
                               result.medium_high_mem_count, result.high_mem_count])
            line_data.append(round((result.lower_mem_count * 100.0) / total_count, 2))
            line_data.append(round((result.medium_lower_mem_count * 100.0) / total_count, 2))
            line_data.append(round((result.medium_high_mem_count * 100.0) / total_count, 2))
            line_data.append(round((result.high_mem_count * 100.0) / total_count, 2))
            ret_list.append(line_data)
        title_name = ["服务器名称", "10>内存资源利用率", "50>内存资源利用率>=10", "90>内存资源利用率>=50", "内存资源利用率>=90"]
        return output_table_excel("内存", title_name, ret_list)


if __name__ == '__main__':
    ResourceUtilizationInitialMgr().resouce_utilization()
