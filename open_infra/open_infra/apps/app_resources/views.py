# Create your views here.
# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: views.py
# @Software: PyCharm
import json
from datetime import datetime
from django.db import transaction
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework_simplejwt import authentication
from app_resources.models import ServiceInfo, ServiceSla, ServiceImage, HWCloudAccount, HWCloudEipInfo, ServiceIntroduce
from app_resources.resources.account_mgr import AccountMgr
from app_resources.resources.eip_mgr import EipMgr
from app_resources.resources.sla_mgr import SlaMgr
from open_infra.utils.common import assemble_api_result, list_param_check_and_trans
from open_infra.utils.api_error_code import ErrCode
from django.conf import settings
from logging import getLogger
from rest_framework.viewsets import GenericViewSet

logger = getLogger("django")


class IndexView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def list(self, request):
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
class AccountView(GenericViewSet):
    """get the all account info"""

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def list(self, request):
        account_mgr = AccountMgr()
        clouds_account = account_mgr.get_cloud_account()
        return clouds_account


# noinspection DuplicatedCode,PyMethodMayBeStatic
class EipView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def list(self, request):
        """get the list of eip"""
        params_dict = list_param_check_and_trans(request.GET.dict())
        eip_mgr = EipMgr()
        data = eip_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


# noinspection DuplicatedCode,PyMethodMayBeStatic
class ServiceView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        """get the list of serive"""
        dict_data = request.GET.dict()
        params_dict = list_param_check_and_trans(dict_data, order_by="service_name")
        filter_name, filter_value = dict_data.get("filter_name"), dict_data.get("filter_value")
        cluster = dict_data.get("cluster")
        region = dict_data.get("region")
        community = dict_data.get("community")
        base_image = dict_data.get("base_image")
        base_os = dict_data.get("base_os")
        if filter_name:
            params_dict["filter_name"] = filter_name.strip()
            params_dict["filter_value"] = filter_value.strip()
        if cluster:
            params_dict["cluster"] = cluster.strip()
        if region:
            params_dict["region"] = region.strip()
        if community:
            params_dict["community"] = community.strip()
        if base_image:
            params_dict["base_image"] = base_image.strip()
        if base_os:
            params_dict["base_os"] = base_os.strip()
        sla_mgr = SlaMgr()
        data = sla_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)

    def post(self, request):
        """create the service sla and sla image, sla
        body:
        {
            "service_name":"service_name",
            "namespace": "namespace",
            "region":  "region",
            "cluster": "cluster",
            "community": "community",
            "image": [
                {
                    "image":
                    "cpu_limit":
                    "mem_limit":
                }
            ]
        }
        """
        dict_data = json.loads(request.body)
        service_name = dict_data.get("service_name")
        namespace = dict_data.get("namespace")
        cluster = dict_data.get("cluster")
        region = dict_data.get("region")
        community = dict_data.get("community")
        image_list = dict_data.get("image")
        if not all([service_name, namespace, cluster, region, community, image_list]):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if not isinstance(image_list, list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        for image in image_list:
            image_name = image.get("image")
            cpu_limit = image.get("cpu_limit")
            mem_limit = image.get("mem_limit")
            if not all([image_name, cpu_limit, mem_limit]):
                return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        service_obj = ServiceInfo.create_single(service_name=service_name, namespace=namespace, cluster=cluster,
                                                region=region, community=community)
        with transaction.atomic():
            for image in image_list:
                ServiceImage.create_single(image=image["image"], cpu_limit=image["cpu_limit"],
                                           mem_limit=image["mem_limit"], service=service_obj)
        return assemble_api_result(ErrCode.STATUS_SUCCESS)


class DetailServiceView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

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


class SeviceExportView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        """get the file excel of sla"""
        dict_data = request.GET.dict()
        params_dict = list_param_check_and_trans(dict_data, order_by="service_name")
        filter_name, filter_value = dict_data.get("filter_name"), dict_data.get("filter_value")
        cluster = dict_data.get("cluster")
        region = dict_data.get("region")
        community = dict_data.get("community")
        base_image = dict_data.get("base_image")
        base_os = dict_data.get("base_os")
        if filter_name:
            params_dict["filter_name"] = filter_name.strip()
            params_dict["filter_value"] = filter_value.strip()
        if cluster:
            params_dict["cluster"] = cluster.strip()
        if region:
            params_dict["region"] = region.strip()
        if community:
            params_dict["community"] = community.strip()
        if base_image:
            params_dict["base_image"] = base_image.strip()
        if base_os:
            params_dict["base_os"] = base_os.strip()
        sla_mgr = SlaMgr()
        data = sla_mgr.export_service(params_dict)
        res = HttpResponse(content=data, content_type="application/octet-stream")
        now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = "service_info_{}".format(now_date)
        res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
        res['charset'] = 'utf-8'
        return res


class NameSpaceView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        """get all namespace"""
        sla_mgr = SlaMgr()
        data = sla_mgr.get_all_namespace()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class ClusterView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        """get all cluster"""
        sla_mgr = SlaMgr()
        data = sla_mgr.get_all_cluster()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class RegionView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        """get all region"""
        sla_mgr = SlaMgr()
        data = sla_mgr.get_all_region()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class CommunityView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        """get all community"""
        sla_mgr = SlaMgr()
        data = sla_mgr.get_all_community()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class BaseOsView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        list_data = ServiceImage.get_all_base_os()
        list_data = [{"label": i["base_os"], "value": i["base_os"]} for i in list_data if i["base_os"]]
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=list_data)


class BaseImageView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        list_data = ServiceImage.get_all_base_image()
        list_data = [{"label": i["base_image"], "value": i["base_image"]} for i in list_data if i["base_image"]]
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=list_data)


# noinspection DuplicatedCode,PyMethodMayBeStatic
class SlaExportView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

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


class ServiceIntroduceView(GenericViewSet):
    """get the service introduce by es"""
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        data = [{
            "name": i.service_name,
            "introduce": i.service_introduce,
            "lang": i.service_lang,
            "url": i.service_sla.url,
            "zone": i.service_sla.service_zone,
        } for i in ServiceIntroduce.all()]
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class RepoView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        list_data = ServiceImage.get_image()
        set_data, ret_data = set(), list()
        for i in list_data:
            if i["repository"]:
                if i["repository"].endswith(".git"):
                    repo = i["repository"]
                else:
                    repo = "{}.git".format(i["repository"])
                set_data.add((repo, i["branch"], i["developer"], i["email"]))
        for data in list(set_data):
            dict_data = dict()
            dict_data["repository"] = data[0]
            dict_data["branch"] = data[1]
            dict_data["developer"] = data[2]
            dict_data["email"] = data[3]
            ret_data.append(dict_data)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=ret_data)
