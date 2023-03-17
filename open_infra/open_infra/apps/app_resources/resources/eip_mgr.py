# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 14:27
# @Author  : Tom_zc
# @FileName: eip_mgr.py
# @Software: PyCharm
from app_resources.models import HWCloudEipInfo
from open_infra.utils.common import get_suitable_range


class EipMgr:
    def list(self, kwargs):
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        eip_list = HWCloudEipInfo.filter(filter_name, filter_value)
        total = len(eip_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "create_time"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        eip_list = eip_list.order_by(order_by)
        task_list = [task.to_dict() for task in eip_list[slice_obj]]
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": task_list
        }
        return res
