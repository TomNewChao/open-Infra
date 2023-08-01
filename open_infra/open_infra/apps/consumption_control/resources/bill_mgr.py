# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 14:55
# @Author  : Tom_zc
# @FileName: bill_mgr.py
# @Software: PyCharm
import datetime
import time
import traceback
from collections import defaultdict
from django.conf import settings
from django.db import transaction
from app_resources.resources.account_mgr import AccountMgr
from consumption_control.models import HWCloudBillInfo
from open_infra.libs.lib_cloud import HWCloudBSSIntl, HWCloudBSS
from open_infra.utils.common import get_month_range, format_float, get_suitable_range
from logging import getLogger

logger = getLogger("django")


class BillMgr:
    def parse_bill_list(self, bill_list, is_intl):
        dict_data = defaultdict(float)
        for i in bill_list:
            if int(i.consume_amount) == 0:
                continue
            elif is_intl:
                bill_cycle = i.bill_cycle
                resource_type_name = settings.BILL_INTL_ALIAS.get(i.resource_type_name)
                if resource_type_name is None:
                    logger.error(
                        "[BillMgr] parse resource_type_name:{} failed, must be adapter.".format(i.resource_type_name))
                    resource_type_name = "unknown"
            else:
                bill_cycle = i.bill_cycle
                resource_type_name = i.resource_type_name
            key = (bill_cycle, resource_type_name)
            dict_data[key] += float(i.consume_amount)
        return dict_data

    def get_bill_cycle(self):
        cur_date = time.localtime()
        cur_year = cur_date.tm_year
        cur_month = cur_date.tm_mon
        cur_day = cur_date.tm_wday
        start_day = datetime.date(2020, 1, 1)
        if int(cur_month) == 1:
            end_day = datetime.date(cur_year - 1, 12, cur_day)
        else:
            end_day = datetime.date(cur_year, cur_month - 1, cur_day)
        cur_bill_cycle_list = get_month_range(start_day, end_day)
        return cur_bill_cycle_list

    def scan_bill(self):
        account_info = AccountMgr.get_decrypt_hw_account_project_info_from_database()
        for config_item in account_info:
            try:
                ak = config_item["ak"]
                sk = config_item["sk"]
                account = config_item['account']
                bill_cycle_list = HWCloudBillInfo.query_bill_by_account(account)
                bill_set = set([bill["bill_cycle"] for bill in bill_cycle_list])
                cur_bill_cycle_list = set(self.get_bill_cycle())
                need_create_list = list(cur_bill_cycle_list - bill_set)
                is_intl = account in settings.BILL_INTL_ACCOUNT
                if is_intl:
                    hw_cloud_bss = HWCloudBSSIntl(ak, sk)
                else:
                    hw_cloud_bss = HWCloudBSS(ak, sk)
                bill_info_list = list()
                for bill_cycle in need_create_list:
                    bill_cycle_temp = hw_cloud_bss.get_bill_list(bill_cycle)
                    bill_info_list.extend(bill_cycle_temp)
                bill_dict_list = self.parse_bill_list(bill_info_list, is_intl)
                with transaction.atomic():
                    for key, value in bill_dict_list.items():
                        if int(value) == 0:
                            continue
                        elif value < 0:
                            rate = 0
                            consume_amount = round(value, 2)
                            actual_cost = consume_amount
                        elif is_intl:
                            rate = settings.BILL_RATE["interational"]
                            consume_amount = round(value * settings.USD_EXCHANGE_RATE, 2)
                            actual_cost = round(rate * consume_amount, 2)
                        elif key[1] in settings.BILL_BRANDWIDTH_LIST:
                            rate = settings.BILL_RATE["brandwidth"]
                            consume_amount = round(value, 2)
                            actual_cost = round(rate * consume_amount, 2)
                        else:
                            rate = settings.BILL_RATE["common"]
                            consume_amount = round(value, 2)
                            actual_cost = round(rate * consume_amount, 2)
                        HWCloudBillInfo.objects.create(
                            bill_cycle=key[0],
                            account=account,
                            resource_type_name=key[1],
                            consume_amount=consume_amount,
                            discount_rate=rate,
                            actual_cost=actual_cost,
                        )
            except Exception as e:
                logger.error("[BillMgr] error:{}, traceback:{}".format(e, traceback.format_exc()))

    def list(self, kwargs):
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        resource_type = kwargs.get("resource_type")
        account = kwargs.get("account")
        bill_info_list = HWCloudBillInfo.filter(filter_name, filter_value)
        if resource_type:
            if not resource_type.isdigit():
                bill_info_list = bill_info_list.filter(resource_type_name=resource_type)
            else:
                bill_info_list = bill_info_list.filter(resource_type_name=None)
        if account:
            if not account.isdigit():
                bill_info_list = bill_info_list.filter(account=account)
            else:
                bill_info_list = bill_info_list.filter(account=None)
        total = len(bill_info_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "account"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        bill_list = bill_info_list.order_by(order_by)
        task_list = [task.to_dict() for task in bill_list[slice_obj]]
        total_consume_amount = round(sum([float(task.consume_amount) for task in bill_list]), 2)
        total_actual_cost = round(sum([task.actual_cost for task in bill_list]), 2)
        res = {
            "size": size,
            "page": page,
            "total": total,
            "total_consume_amount": format_float(total_consume_amount),
            "total_actual_cost": format_float(total_actual_cost),
            "data": task_list
        }
        return res

    def get_all_account(self):
        """query all account from mysql"""
        account_list = HWCloudBillInfo.count_acount()
        ret_list = list()
        for account in account_list:
            dict_data = dict()
            if account["account"]:
                dict_data["label"] = account["account"]
                dict_data["value"] = account["account"]
            else:
                dict_data["label"] = '空'
                dict_data["value"] = '0'
            ret_list.append(dict_data)
        return ret_list

    def get_all_resource_type_name(self):
        """query all resource_type_name from mysql"""
        resource_type_name_list = HWCloudBillInfo.count_resource_type_name()
        ret_list = list()
        for resource_type_name in resource_type_name_list:
            dict_data = dict()
            if resource_type_name["resource_type_name"]:
                dict_data["label"] = resource_type_name["resource_type_name"]
                dict_data["value"] = resource_type_name["resource_type_name"]
            else:
                dict_data["label"] = '空'
                dict_data["value"] = '0'
            ret_list.append(dict_data)
        return ret_list

    def get_year_amount(self, year):
        cur_date = time.localtime()
        cur_year = cur_date.tm_year
        cur_month = cur_date.tm_mon
        if cur_year == year:
            end_day = datetime.date(year, cur_month, 1)
        else:
            end_day = datetime.date(year, 12, 1)
        start_day = datetime.date(year, 1, 1)
        month_list = get_month_range(start_day, end_day)
        sorted_month_list = sorted(month_list)
        account_list = HWCloudBillInfo.count_acount()
        dict_data = dict()
        for account in account_list:
            dict_bill, list_bill = dict(), list()
            account_name = account["account"]
            bill_list = HWCloudBillInfo.bill_list(account_name, sorted_month_list)
            for i in bill_list:
                dict_bill[i["bill_cycle"]] = round(i["consume"], 2)
            for month in sorted_month_list:
                list_bill.append(dict_bill.get(month, 0))
            dict_data[account_name] = list_bill
        return dict_data

    def get_month_amount(self, account, bill_cycle):
        bill_list = HWCloudBillInfo.count_consume_type(account, bill_cycle)
        sum_amount_obj = HWCloudBillInfo.count_actual_cost(account, bill_cycle)
        if sum_amount_obj["actual_cost__sum"] is None:
            return list()
        sum_amount = round(float(sum_amount_obj["actual_cost__sum"]), 2)
        ret_list = [{"name": i["resource_type_name"], "value": round(float(i["consume"]), 2)} for i in bill_list]
        top_amount_sum = sum([i["value"] for i in ret_list])
        other_value = round(sum_amount - top_amount_sum, 2)
        if other_value != 0:
            other_dict = {"name": "other", "value": other_value}
            ret_list.append(other_dict)
        return ret_list

    def get_all_bill_cycle(self):
        all_bill_list = HWCloudBillInfo.count_bill_cycle()
        ret_list = list()
        cur = datetime.datetime.now()
        cur_year = cur.year
        cur_month = cur.month
        if int(cur_month) == 1:
            dict_data = dict()
            dict_data["title"] = "{}-0{}".format(cur_year, cur_month)
            dict_data["key"] = "{}-0{}".format(cur_year, cur_month)
            ret_list.append(dict_data)
        for bill_cycle_obj in all_bill_list:
            dict_data = dict()
            dict_data["title"] = bill_cycle_obj["bill_cycle"]
            dict_data["key"] = bill_cycle_obj["bill_cycle"]
            ret_list.append(dict_data)
        return ret_list

    def get_all_year(self):
        all_bill_list = HWCloudBillInfo.count_bill_cycle()
        year_set = set()
        ret_list = list()
        cur_year = datetime.datetime.now().year
        year_set.add(str(cur_year))
        for bill_cycle_obj in all_bill_list:
            year_set.add(bill_cycle_obj["bill_cycle"].split("-")[0])
        year_list = sorted(list(year_set), reverse=True)
        for year_temp in year_list:
            dict_data = dict()
            dict_data["title"] = int(year_temp)
            dict_data["key"] = int(year_temp)
            ret_list.append(dict_data)
        return ret_list
