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

from clouds_tools.models import MemResourceUtilization, CpuResourceUtilization
from clouds_tools.resources.clouds_tools_alarm import ResourceUtilizationAlarm
from open_infra.utils.common import func_retry

logger = logging.getLogger("django")


class AlarmHandlerRangeConfig(object):
    node_cpu_query = "{}/api/v1/query_range?query=node_cpu_seconds_total&start={}&end={}&step={}"
    node_mem_query = "{}/api/v1/query_range?query=node_memory_MemUsed&start={}&end={}&step={}"
    ALARM_PROMETHEUS_URL = "https://monitor.osinfra.cn"
    RANGE_TIME = 7 * 24 * 60 * 60
    STEP = 2 * 60
    EXPIRED_DAY =  6 * 30 * 24 * 60 * 60


class ResourceUtilizationMgr:
    def __init__(self):
        super(ResourceUtilizationMgr, self).__init__()

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

    @func_retry(delay=10)
    def resouce_utilization(self):
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
        CpuResourceUtilization.objects.filter(create_time__lt=expire_timestamps).delete()
        MemResourceUtilization.objects.filter(create_time__lt=expire_timestamps).delete()
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
            logger.error("1------------------{}".format(cpu_value_list))
            logger.error("2------------------{}".format(lower_cpu_count))
            logger.error("3------------------{}".format(medium_lower_cpu_count))
            logger.error("4------------------{}".format(medium_high_cpu_count))
            logger.error("5------------------{}".format(high_cpu_count))

            params = {
                "name": name,
                "lower_cpu_count": lower_cpu_count,
                "medium_lower_cpu_count": medium_lower_cpu_count,
                "medium_high_cpu_count": medium_high_cpu_count,
                "high_cpu_count": high_cpu_count,
                "create_time": int(cur_time),
            }
            CpuResourceUtilization.objects.create(**params)
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
            MemResourceUtilization.objects.create(**params)
        unexcept_name_list = list(set(mem_dict.keys()) - set(cpu_dict.keys()))
        for name in unexcept_name_list:
            logger.info("[resouce_utilization] prom exist in mem and not in cpu:{}".format(name))
        logger.error("-------------------spend time:{}-----------------".format(int(time.time()-cur_time)))


if __name__ == '__main__':
    ResourceUtilizationMgr().resouce_utilization()
