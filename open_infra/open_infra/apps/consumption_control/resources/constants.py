# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 17:52
# @Author  : Tom_zc
# @FileName: constants.py
# @Software: PyCharm
class AlarmHandlerRangeConfig(object):
    node_cpu_query = "{}/api/v1/query_range?query=node_cpu_seconds_total&start={}&end={}&step={}"
    node_mem_query = "{}/api/v1/query_range?query=node_memory_MemUsed&start={}&end={}&step={}"
    ALARM_PROMETHEUS_URL = "https://monitor.osinfra.cn"
    RANGE_TIME = 7 * 24 * 60 * 60
    STEP = 2 * 60
    EXPIRED_DAY = 6 * 30 * 24 * 60 * 60