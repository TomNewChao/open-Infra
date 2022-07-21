import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

from django.views.generic import View
from open_infra.apps.clouds_tools.resources.scan_ports import ScanPorts
from open_infra.utils.common import assemble_api_result
from open_infra.utils.api_error_code import ErrCode


class ScanPortView(View):
    def get(self, request):
        """get all account"""
        scan_ports = ScanPorts()
        clouds_account = scan_ports.get_cloud_account()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=clouds_account)

    def post(self, request):
        """output a file"""
        dict_data = request.POST
        user_name = request.user.username
        if dict_data.get("account") is None or not isinstance(dict_data["account"], list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        scan_ports = ScanPorts()
        is_handler = scan_ports.start_collect_thread(dict_data["account"], user_name)
        if not is_handler:
            err_code = ErrCode.STATUS_SUCCESS
        else:
            err_code = ErrCode.STATUS_SCAN_PORT_ING
        return assemble_api_result(err_code)


class ScanPortProgressView(View):
    "query download progress"

    def get(self, request):
        user_name = request.user.username
        scan_ports = ScanPorts()
        progress, data = scan_ports.query_progress(user_name)
        if progress == 0:
            return assemble_api_result(ErrCode.STATUS_SCAN_PORT_ING)
        elif progress == 1:
            return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)
        else:
            return assemble_api_result(ErrCode.STATUS_SCAN_PORT_FAILED)
