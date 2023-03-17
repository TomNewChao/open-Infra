# Create your views here.
# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: views.py
# @Software: PyCharm
from datetime import datetime
from django.http import HttpResponse
from app_resources.models import ServiceInfo, ServiceSla, ServiceImage, HWCloudAccount, HWCloudEipInfo
from app_resources.resources.account_mgr import AccountMgr
from app_resources.resources.eip_mgr import EipMgr
from app_resources.resources.sla_mgr import SlaMgr
from open_infra.utils.auth_permisson import AuthView
from open_infra.utils.common import assemble_api_result, list_param_check_and_trans
from open_infra.utils.api_error_code import ErrCode
from django.conf import settings
from logging import getLogger

logger = getLogger("django")


class IndexView(AuthView):
    def get(self, request):
        account_count_dict = HWCloudAccount.count_account()
        service_count_dict = ServiceInfo.count_id()
        eip_count_dict = HWCloudEipInfo.count_id()
        data = {
            "account": account_count_dict["count"],
            "service": service_count_dict["count"],
            "eip": eip_count_dict["count"],
        }
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


# noinspection DuplicatedCode,PyMethodMayBeStatic
class AccountView(AuthView):
    """get the all account info"""

    def get(self, request):
        account_mgr = AccountMgr()
        clouds_account = account_mgr.get_cloud_account()
        return clouds_account


# noinspection DuplicatedCode,PyMethodMayBeStatic
class EipView(AuthView):
    def get(self, request):
        """get the list of eip"""
        params_dict = list_param_check_and_trans(request.GET.dict())
        eip_mgr = EipMgr()
        data = eip_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


# noinspection DuplicatedCode,PyMethodMayBeStatic
class ServiceView(AuthView):
    def get(self, request):
        """get the list of serive"""
        dict_data = request.GET.dict()
        params_dict = list_param_check_and_trans(dict_data, order_by="service_name")
        filter_name, filter_value = dict_data.get("filter_name"), dict_data.get("filter_value")
        cluster = dict_data.get("cluster")
        region = dict_data.get("region")
        if filter_name:
            params_dict["filter_name"] = filter_name.strip()
            params_dict["filter_value"] = filter_value.strip()
        if cluster:
            params_dict["cluster"] = cluster.strip()
        if region:
            params_dict["region"] = region.strip()
        sla_mgr = SlaMgr()
        data = sla_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class DetailServiceView(AuthView):
    def get(self, request):
        """get the detail of service"""
        dict_data = request.GET.dict()
        service_id = dict_data.get("id")
        if service_id is None:
            return assemble_api_result(err_code=ErrCode.STATUS_PARAMETER_ERROR)
        service_info = ServiceInfo.objects.get(id=service_id)
        service_dict = service_info.to_dict()
        service_dict["service_image"] = [image_info.to_dict() for image_info in
                                         ServiceImage.objects.filter(service_id=service_id)]
        service_dict["service_sla"] = [sla_info.to_dict() for sla_info in
                                       ServiceSla.objects.filter(service_id=service_id)]
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=service_dict)


class NameSpaceView(AuthView):
    def get(self, request):
        """get all namespace"""
        sla_mgr = SlaMgr()
        data = sla_mgr.get_all_namespace()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class ClusterView(AuthView):
    def get(self, request):
        """get all cluster"""
        sla_mgr = SlaMgr()
        data = sla_mgr.get_all_cluster()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class RegionView(AuthView):
    def get(self, request):
        """get all cluster"""
        sla_mgr = SlaMgr()
        data = sla_mgr.get_all_region()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


# noinspection DuplicatedCode,PyMethodMayBeStatic
class SlaExportView(AuthView):
    def get(self, request):
        """get the file excel of sla"""
        sla_mgr = SlaMgr()
        data = sla_mgr.export()
        res = HttpResponse(content=data, content_type="application/octet-stream")
        now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = settings.CLA_EXCEL_NAME.format(now_date)
        res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
        res['charset'] = 'utf-8'
        return res
