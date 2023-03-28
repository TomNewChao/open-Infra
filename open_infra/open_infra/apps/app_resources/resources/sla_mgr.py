# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 14:27
# @Author  : Tom_zc
# @FileName: sla_mgr.py
# @Software: PyCharm
import datetime
from django.conf import settings
from app_resources.models import ServiceInfo, ServiceImage, ServiceSla
from open_infra.tools.scan_sla import scan_cla
from open_infra.utils.common import output_cla_excel, get_suitable_range
from logging import getLogger

logger = getLogger("django")


class SlaMgr:
    _ignore_service_name_alias = ["Ascend-repo", "openEuler Jenkins ISO", "Ptadapter Jenkins"]

    def query_all_sla_info(self):
        """query all sla info from uptime-robot"""
        cur_date = datetime.datetime.now()
        logger.info("[SlaMgr] query_all_sla_info query year:{} month:{} day:{}".format(cur_date.year, cur_date.month,
                                                                                       cur_date.day))
        sla_detail_list = scan_cla(year=int(cur_date.year), month=int(cur_date.month), day=int(cur_date.day))
        all_sla_list = list()
        for sla_temp in sla_detail_list:
            ret_dict = dict()
            del sla_temp[0]
            if sla_temp[0] in self._ignore_service_name_alias:
                continue
            ret_dict["service_alias"] = sla_temp[0]
            ret_dict["url"] = sla_temp[-1]
            ret_dict["service_zone"] = settings.CLA_EXPLAIN.get(sla_temp[3].lower())
            ret_dict["month_abnormal_time"] = sla_temp[4]
            ret_dict["year_abnormal_time"] = sla_temp[5]
            ret_dict["month_sla"] = sla_temp[6].replace("%", "")
            ret_dict["year_sla"] = sla_temp[7].replace("%", "")
            ret_dict["remain_time"] = round(sla_temp[8], 4)
            all_sla_list.append(ret_dict)
        return all_sla_list

    def get_all_namespace(self):
        """query all namespace from mysql"""
        namespace_list = ServiceInfo.objects.order_by("namespace").values("namespace").distinct()
        ret_list = list()
        for namespace in namespace_list:
            dict_data = dict()
            if namespace["namespace"]:
                dict_data["label"] = namespace["namespace"]
                dict_data["value"] = namespace["namespace"]
            else:
                dict_data["label"] = '空'
                dict_data["value"] = '0'
            ret_list.append(dict_data)
        return ret_list

    def get_all_cluster(self):
        """query all cluster from mysql"""
        cluster_list = ServiceInfo.objects.order_by("cluster").values("cluster").distinct()
        ret_list = list()
        for cluster in cluster_list:
            dict_data = dict()
            if cluster["cluster"]:
                dict_data["label"] = cluster["cluster"]
                dict_data["value"] = cluster["cluster"]
            else:
                dict_data["label"] = '空'
                dict_data["value"] = '0'
            ret_list.append(dict_data)
        return ret_list

    def get_all_region(self):
        """query all cluster from mysql"""
        cluster_list = ServiceInfo.objects.order_by("region").values("region").distinct()
        ret_list = list()
        for cluster in cluster_list:
            dict_data = dict()
            if cluster["region"]:
                dict_data["label"] = cluster["region"]
                dict_data["value"] = cluster["region"]
            else:
                dict_data["label"] = '空'
                dict_data["value"] = '0'
            ret_list.append(dict_data)
        return ret_list

    def list(self, kwargs):
        """The list of service"""
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        cluster = kwargs.get("cluster")
        region = kwargs.get("region")
        service_info_list = ServiceInfo.filter(filter_name, filter_value)
        if cluster:
            if cluster != '0':
                service_info_list = service_info_list.filter(cluster=cluster)
            else:
                service_info_list = service_info_list.filter(cluster='')
        if region:
            if region != '0':
                service_info_list = service_info_list.filter(region=region)
            else:
                service_info_list = service_info_list.filter(region='')
        total = len(service_info_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "create_time"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        service_result_list = service_info_list.order_by(order_by)[slice_obj]
        service_list = list()
        for service_info in service_result_list:
            service_dict = service_info.to_dict()
            service_id = service_dict["id"]
            service_dict["base_image"] = ",".join(
                [service_image['base_image'] for service_image in ServiceImage.get(service_id, "base_image")
                 if service_image['base_image']])
            service_dict["base_os"] = ",".join(
                [service_image['base_os'] for service_image in ServiceImage.get(service_id, "base_os")
                 if service_image['base_os']])
            service_dict["repository"] = ",".join(
                [service_image['repository'] for service_image in ServiceImage.get(service_id, "repository")
                 if service_image['repository']])
            service_dict["image"] = ",".join(
                [service_image['image'] for service_image in ServiceImage.get(service_id, "image")
                 if service_image['image']])
            service_list.append(service_dict)
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": service_list
        }
        return res

    def export(self):
        service_info_list = ServiceSla.all()
        return output_cla_excel(service_info_list)
