# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 10:44
# @Author  : Tom_zc
# @FileName: views.py
# @Software: PyCharm
import json
import logging
import traceback
from django.db import transaction
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions
from rest_framework_simplejwt import authentication
from open_infra.utils.api_error_code import ErrCode
from open_infra.utils.common import assemble_api_result, list_param_check_and_trans
from open_infra.utils.utils_git import GitHubPrStatus
from open_infra.utils.utils_kubeconfig import KubeconfigLib
from permission.models import KubeConfigInfo
from permission.resources.constants import PrComment, KubeConfigRole, KubeConfigLock
from permission.resources.permission_mgr import KubeConfigGitBase, KubeconfigEmailTool, KubeconfigMgr
from django.utils import timezone

logger = logging.getLogger("django")


# noinspection PyMethodMayBeStatic
class KubeConfigGitView(GenericViewSet):
    def post(self, request):
        """this api is to receive the pr request from github： kubeconfig-interact
           Detail: https://github.com/Open-Infra-Ops/kubeconfig-interact
        """
        dict_data = json.loads(request.body)
        if not GitHubPrStatus.is_in_github_pr_status(dict_data.get("action")):
            logger.error("[GitHubPrView] receive param fault:{}".format(dict_data.get("action")))
            return assemble_api_result(err_code=ErrCode.STATUS_SUCCESS)
        github_pr = KubeConfigGitBase(dict_data)
        try:
            # new pr
            if GitHubPrStatus.is_in_new_pr_status(dict_data["action"]) and dict_data.get("pull_request") is not None:
                is_ok, msg, _ = github_pr.parse_create_pr()
                username = dict_data["pull_request"]["user"]["login"]
                comment = PrComment.welcome.format(username, is_ok, msg)
                github_pr.comment_pr(comment)
            # comment
            elif dict_data["action"] == GitHubPrStatus.create and dict_data["comment"].get("body") == "/check":
                is_ok, msg, _ = github_pr.parse_create_pr()
                username = dict_data["issue"]["user"]["login"]
                comment = PrComment.welcome.format(username, is_ok, msg)
                github_pr.comment_pr(comment)
            # merge
            elif dict_data["action"] == GitHubPrStatus.closed and dict_data["pull_request"]["merged"]:
                logger.info("start to merge...............")
                is_ok, msg, list_data = github_pr.parse_create_pr()
                create_time = dict_data["pull_request"]["created_at"]
                merge_at = dict_data["pull_request"]["merged_at"]
                with KubeConfigLock.ProcessLock:
                    for kubeconfig_info in list_data:
                        KubeconfigMgr.create_kubeconfig(kubeconfig_info, dict_data, create_time, merge_at)
        except Exception as e:
            logger.error("[GitHubPrView] e:{}, traceback:{}".format(e, traceback.format_exc()))
            github_pr.comment_pr(comment=PrComment.error)
        return assemble_api_result(err_code=ErrCode.STATUS_SUCCESS)


# noinspection PyMethodMayBeStatic
class KubeConfigView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        """get the detail of kubeconfig"""
        dict_data = request.GET.dict()
        config_id = dict_data.get("id")
        if not config_id or not config_id.isdigit():
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            kubeconfig_info = KubeConfigInfo.objects.get(id=config_id)
            ret_dict = kubeconfig_info.to_dict()
        except KubeConfigInfo.DoesNotExist as e:
            logger.error("[KubeConfigView] e:{}".format(e))
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=ret_dict)

    def put(self, request):
        """modify kubeconfig"""
        dict_data = json.loads(request.body)
        config_id = dict_data.get("id")
        role = dict_data.get("role")
        expired_time = dict_data.get("expired_time")
        if not all([config_id, role, expired_time]):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if not KubeConfigRole.is_in_kubeconfig_role(role):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if int(expired_time) <= 0:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            config_obj = KubeConfigInfo.objects.get(id=config_id)
            cluster, namespace = config_obj.service_name.split("_")
            # If the roles are the same, modify the expiration time, The roles are different, they are all modified
            if config_obj.role == role and (int(config_obj.expired_time) == int(expired_time)):
                logger.info("[KubeConfigView] modify the kubeconfig params consistency...")
            elif config_obj.role == role:
                KubeConfigInfo.objects.filter(id=config_id).update(expired_time=int(expired_time))
            else:
                with KubeConfigLock.ProcessLock:
                    cur_time = timezone.now()
                    need_create = dict()
                    with transaction.atomic():
                        need_create["username"] = config_obj.username
                        need_create["role"] = config_obj.role
                        need_create["namespace"] = namespace
                        need_create["cluster"] = cluster
                        KubeconfigLib.delete_kubeconfig(need_create)
                        need_create["role"] = role
                        is_ok, content = KubeconfigLib.create_kubeconfig(need_create)
                        if not is_ok:
                            raise Exception("[KubeConfigView] create kubeconfig:{}".format(content))
                        email_list = [config_obj.email, ]
                        need_create["create_time"] = config_obj.create_time
                        need_create["review_time"] = config_obj.review_time
                        need_create["expired_time"] = int(expired_time)
                        need_create["namespace"] = namespace
                        need_create["attachment_content"] = content
                        is_send_ok = KubeconfigEmailTool.send_kubeconfig_email(need_create, email_list)
                        KubeConfigInfo.objects.filter(id=config_id).update(expired_time=int(expired_time), role=role,
                                                                           modify_time=cur_time, send_ok=is_send_ok)
        except Exception as e:
            logger.error("AlarmEmailListView {}".format(e))
            return assemble_api_result(ErrCode.INTERNAL_ERROR)
        return assemble_api_result(ErrCode.STATUS_SUCCESS)


# noinspection PyMethodMayBeStatic
class BatchKubeConfigView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request):
        """get the list of kubeconfig"""
        params_dict = list_param_check_and_trans(request.GET.dict(), order_by="create_time")
        kubeconfig_mgr = KubeconfigMgr()
        data = kubeconfig_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)

    def post(self, request):
        """batch delete kubeconfig"""
        dict_data = json.loads(request.body)
        kubeconfig_ids = dict_data.get("kubeconfig_ids")
        if kubeconfig_ids is None or not isinstance(kubeconfig_ids, list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        with KubeConfigLock.ProcessLock:
            kubeconfig_list = KubeConfigInfo.objects.filter(id__in=kubeconfig_ids)
            failed_dict = dict()
            with transaction.atomic():
                for kubeconfig in kubeconfig_list:
                    try:
                        cluster, namespace = kubeconfig.service_name.split("_")
                        dict_data = dict()
                        dict_data["namespace"] = namespace
                        dict_data["cluster"] = cluster
                        dict_data["role"] = kubeconfig.role
                        dict_data["username"] = kubeconfig.username
                        KubeconfigLib.delete_kubeconfig(dict_data)
                        KubeConfigInfo.objects.filter(id=kubeconfig.id).delete()
                    except Exception as e:
                        failed_dict[kubeconfig.username] = kubeconfig.service_name
                        logger.error("[BatchKubeConfigView] delete kubeconfig:{}, traceback:{}".format(e,
                                                                                                       traceback.format_exc()))
        if failed_dict:
            return assemble_api_result(ErrCode.STATUS_KUBECONFIG_DELETE_FAILED, trans_para=str(failed_dict))
        return assemble_api_result(ErrCode.STATUS_SUCCESS)
