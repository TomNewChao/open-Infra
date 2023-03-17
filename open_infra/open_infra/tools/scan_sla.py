# -*- coding: utf-8 -*-
# @Time    : 2022/8/24 16:57
# @Author  : Tom_zc
# @FileName: scan_sla.py
# @Software: PyCharm

import calendar
import logging
import json
import subprocess
import time
from urllib.parse import urlparse
from django.conf import settings

logger = logging.getLogger("django")


class ScanClaConfig:
    shell_cmd1 = f'curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Cache-Control: no-cache" -d' \
                 f' "api_key=%s&format=json&logs=1&offset=0"' \
                 f' "https://api.uptimerobot.com/v2/getMonitors"'

    shell_cmd2 = f'curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Cache-Control: no-cache" -d' \
                 f' "api_key=%s&format=json&logs=1&offset=%s"' \
                 f' "https://api.uptimerobot.com/v2/getMonitors"'

    shell_cmd3 = f'curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Cache-Control: no-cache" -d' \
                 f' "api_key=%s&format=json&logs=1&offset=50"' \
                 f' "https://api.uptimerobot.com/v2/getMonitors"'


class ScanClaTools:
    @staticmethod
    def execute_cmd3(cmd):
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        ret_data, _ = r.communicate()
        return ret_data

    @staticmethod
    def get_cla_data(api_key):
        list_data = list()
        ret_data = ScanClaTools.execute_cmd3(ScanClaConfig.shell_cmd1 % api_key)
        ret_data = json.loads(ret_data)
        if ret_data["stat"] != "ok":
            logger.info("[scan_cla] get data failed")
            raise Exception("[get_cla_data] get data failed")
        list_data.extend(ret_data["monitors"])
        offset = ret_data["pagination"]["offset"]
        total = ret_data["pagination"]["total"]
        limit = ret_data["pagination"]["limit"]
        start = offset + limit
        for offset in range(start, total, limit):
            ret_data_temp = ScanClaTools.execute_cmd3(ScanClaConfig.shell_cmd2 % (api_key, offset))
            ret_data_list = json.loads(ret_data_temp)
            if ret_data_list["stat"] != "ok":
                logger.info("[scan_cla] get data failed")
                raise Exception("[get_cla_data] get data failed")
            list_data.extend(ret_data_list["monitors"])
        return list_data


def exec_shell_cmd1(api_key, cur_year, cur_month, cur_day):
    list_data = ScanClaTools.get_cla_data(api_key)
    # 调试将debug_enable置为1
    debug_enable = 0
    # 全年允许异常时间
    if cur_year % 4 == 0 and cur_year % 100 != 0 or cur_year % 400 == 0:
        count_curl_year_sec = 366 * 60 * 60 * 24
    else:
        count_curl_year_sec = 365 * 60 * 60 * 24
    allow_err_time_sec = count_curl_year_sec * 0.001
    allow_err_time_min = count_curl_year_sec / 60 * 0.001
    logger.info(f"全年允许异常时间={allow_err_time_sec}s")
    logger.info(f"全年允许异常时间={allow_err_time_min}min")

    # 确认所需统计月份及天数
    # 如果输入月份小于当前月份，则需要更新该月的总天数
    # 如果输入月份等于当前月份，则根据当前日期，更新当月天数
    t = time.localtime()
    which_today = time.strftime("%j", t)
    logger.info(f"今天是2022年第{which_today}天")
    which_month = time.strftime("%m", t)
    logger.info(f"今天是2022年第{which_month}月")

    count_year_days = 0
    count_month_days = 0
    if cur_month <= int(which_month):
        logger.info(f"本次统计{cur_month}月SLA")
        i = 1
        while i < cur_month:
            _, before_month_days = calendar.monthrange(cur_year, i)
            count_year_days += before_month_days
            i += 1
        count_month_days = cur_day - 1
        count_year_days += count_month_days
    else:
        # 统计本月
        logger.info(f"本次统计{which_month}月SLA")
        # 统计当月的SLA，当月天数为今天的日期-1
        count_month_days = int(time.strftime("%d", t))
        count_month_days -= 1
        # 统计当年的SLA
        count_year_days = int(which_today) - 1

    logger.info(f"统计{cur_month}月{count_month_days}天")
    count_month_mins = count_month_days * 24 * 60
    logger.info(f"统计{cur_month}月总时长{count_month_mins}分钟")
    logger.info("分母是%d", count_year_days)
    if 1 <= cur_month <= 9:
        cur_month = f"0{cur_month}"
    ret_list = list()
    for item in list_data:
        logs_list = item.get("logs")
        sum_year_duration_time_sec = 0
        sum_month_duration_time_sec = 0
        flag_id = item.get("id")
        friendly_name = item.get("friendly_name")
        url = item.get("url")  # 域名
        domain = urlparse(url).netloc
        if url == "mail.mindspore.cn":
            domain = "MindSpore"
        elif url == "mail.opengauss.org":
            domain = "openGauss"
        elif url == "mail.openlookeng.io":
            domain = "openLooKeng"
        elif url == "159.138.46.20":
            domain = "openEuler"
        elif not domain:
            logger.info("url is %s", url)
            continue
        else:
            domain = domain.split(".")[-2]
        if domain == "158":
            domain = "Ascend"
        elif domain == "97":
            domain = "openEuler"
        for log in logs_list:
            str_datetime = log.get("datetime")
            str_datetime = time.strftime('%Y-%m-%d&%H:%M:%S', time.localtime(str_datetime))
            str_month = str_datetime.split("&")[0].split("-")[1]
            str_year = str_datetime.split("&")[0].split("-")[0]
            str_day = str_datetime.split("&")[0].split("-")[2]
            is_equal_month = (
                    str_month == str(cur_month) and int(str_day) <= int(cur_day) and str_year == str(cur_year))
            if (int(str_month) < int(cur_month) and str_year == str(cur_year)) or is_equal_month:
                if log.get("type") == 1:
                    duration = log.get("duration")
                    sum_year_duration_time_sec += duration
                    if debug_enable == 1:
                        ret_list.append([flag_id, friendly_name, domain, str_datetime, round(duration / 60, 1)])
            if str_month == str(cur_month) and str_year == str(cur_year) and int(str_day) <= int(count_month_days):
                if log.get("type") == 1:
                    duration = log.get("duration")
                    sum_month_duration_time_sec += duration
        cur_year_sla = round(1 - int(sum_year_duration_time_sec) / (3600 * 24 * count_year_days), 6)
        cur_year_sla = format(cur_year_sla, '.3%')
        cur_month_sla = round(1 - int(sum_month_duration_time_sec) / (3600 * 24 * count_month_days), 6)
        cur_month_sla = format(cur_month_sla, '.3%')
        # 将异常持续时长单位更换成min
        sum_month_duration_time_min = round(int(sum_month_duration_time_sec) / 60, 1)
        sum_year_duration_time_min = round(int(sum_year_duration_time_sec) / 60, 1)
        free_sla_time_min = allow_err_time_min - sum_year_duration_time_min
        if debug_enable == 1:
            ret_list.append([flag_id, friendly_name, "", "", domain, "", "", sum_month_duration_time_min,
                             sum_year_duration_time_min, cur_month_sla, cur_year_sla, free_sla_time_min])

        else:
            ret_list.append([flag_id, friendly_name, "", "", domain, sum_month_duration_time_min,
                             sum_year_duration_time_min, cur_month_sla, cur_year_sla, free_sla_time_min])
    return ret_list


def exec_shell_cmd2(api_key, cur_year, cur_month, cur_day):
    list_data = ScanClaTools.get_cla_data(api_key)
    # 调试将debug_enable置为1
    debug_enable = 0
    # 全年允许异常时间
    if cur_year % 4 == 0 and cur_year % 100 != 0 or cur_year % 400 == 0:
        count_curl_year_sec = 366 * 60 * 60 * 24
    else:
        count_curl_year_sec = 365 * 60 * 60 * 24
    allow_err_time_sec = count_curl_year_sec * 0.0005
    allow_err_time_min = count_curl_year_sec / 60 * 0.0005
    logger.info(f"全年允许异常时间={allow_err_time_sec}s")
    logger.info(f"全年允许异常时间={allow_err_time_min}min")

    # 确认所需统计月份及天数
    # 如果输入月份小于当前月份，则需要更新该月的总天数
    # 如果输入月份等于当前月份，则根据当前日期，更新当月天数
    t = time.localtime()
    which_today = time.strftime("%j", t)
    logger.info(f"今天是2022年第{which_today}天")
    which_month = time.strftime("%m", t)
    logger.info(f"今天是2022年第{which_month}月")

    count_year_days = 0
    count_month_days = 0
    if cur_month < int(which_month):
        logger.info(f"本次统计{cur_month}月SLA")
        i = 1
        while i <= cur_month:
            _, count_month_days = calendar.monthrange(cur_year, i)
            count_year_days += count_month_days
            i += 1
    else:
        logger.info(f"本次统计{which_month}月SLA")
        # 统计当月的SLA，当月天数为今天的日期-1
        count_month_days = int(time.strftime("%d", t))
        count_month_days -= 1
        if count_month_days == 0:
            cur_month -= 1
            _, count_month_days = calendar.monthrange(cur_year, cur_month)
        count_year_days = int(which_today) - 1

    logger.info(f"统计{cur_month}月{count_month_days}天")
    count_month_mins = count_month_days * 24 * 60
    logger.info(f"统计{cur_month}月总时长{count_month_mins}分钟")

    # count_year_days = int(which_today) - 1
    logger.info("分母是%d", count_year_days)
    if 1 <= cur_month <= 9:
        cur_month = f"0{cur_month}"
    ret_list = list()
    for item in list_data:
        logs_list = item.get("logs")
        sum_year_duration_time_sec = 0
        sum_month_duration_time_sec = 0
        flag_id = item.get("id")
        friendly_name = item.get("friendly_name")
        url = item.get("url")  # 域名
        domain = urlparse(url).netloc

        if url == "mail.mindspore.cn":
            domain = "MindSpore"
        elif url == "mail.opengauss.org":
            domain = "openGauss"
        elif url == "mail.openlookeng.io":
            domain = "openLooKeng"
        elif url == "159.138.46.20":
            domain = "openEuler"
        elif not domain:
            logger.info("url is %s", url)
            continue
        else:
            domain = domain.split(".")[-2]

        if domain == "158":
            domain = "Ascend"
        elif domain == "97":
            domain = "openEuler"
        # domain = domain.split(".")[-2]
        log_type = f"异常"
        for log in logs_list:
            str_datetime = log.get("datetime")
            str_datetime = time.strftime('%Y-%m-%d&%H:%M:%S', time.localtime(str_datetime))
            str_month = str_datetime.split("&")[0].split("-")[1]
            str_year = str_datetime.split("&")[0].split("-")[0]
            str_day = str_datetime.split("&")[0].split("-")[2]
            # 年度SLA统计：
            if str_month <= str(cur_month) and str_year == str(cur_year):
                if log.get("type") == 1:
                    log_id = log.get("id")

                    duration = log.get("duration")
                    sum_year_duration_time_sec += duration
                    # 写入每次异常发生时间，持续时长
                    if debug_enable == 1:
                        ret_list.append([flag_id, friendly_name, domain, str_datetime, round(duration / 60, 1), url])

            # 月度SLA统计
            if str_month == str(cur_month) and str_year == str(cur_year) and str_day <= str(count_month_days):
                if log.get("type") == 1:
                    log_id = log.get("id")
                    duration = log.get("duration")
                    sum_month_duration_time_sec += duration

        cur_year_sla = round(1 - int(sum_year_duration_time_sec) / (3600 * 24 * count_year_days),
                             6)  # 截止统计日前一日的年度SLA
        cur_year_sla = format(cur_year_sla, '.3%')
        cur_month_sla = round(1 - int(sum_month_duration_time_sec) / (3600 * 24 * count_month_days),
                              6)  # 截止统计日前一日月份的SLA
        cur_month_sla = format(cur_month_sla, '.3%')
        avg_sla = round(((1 - int(sum_year_duration_time_sec) / (3600 * 24 * count_year_days)) + (
                1 - int(sum_month_duration_time_sec) / (3600 * 24 * count_month_days))) / 2, 6)
        avg_sla = format(avg_sla, '.3%')

        # 将异常持续时长单位更换成min
        sum_month_duration_time_min = round(int(sum_month_duration_time_sec) / 60, 1)
        sum_year_duration_time_min = round(int(sum_year_duration_time_sec) / 60, 1)
        free_sla_time_min = allow_err_time_min - sum_year_duration_time_min
        if debug_enable == 1:
            ret_list.append(
                [flag_id, friendly_name, "", "", domain, "", "", sum_month_duration_time_min,
                 sum_year_duration_time_min, cur_month_sla, cur_year_sla, free_sla_time_min, url])
        else:
            ret_list.append(
                [flag_id, friendly_name, "", "", domain, sum_month_duration_time_min,
                 sum_year_duration_time_min, cur_month_sla, cur_year_sla, free_sla_time_min, url])
    return ret_list


def scan_cla(year, month, day):
    if month > 12 or month < 1:
        logger.info("input fault month:{}".format(month))
        raise Exception("params failed")
    api_key = settings.CLA_API_KEY
    return exec_shell_cmd2(api_key, year, month, day)


if __name__ == '__main__':
    ret_list = scan_cla(2022, 8, 25)
    print(ret_list)
