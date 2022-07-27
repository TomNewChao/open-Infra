import json
from datetime import datetime

from django.http import HttpResponse
from clouds_tools.resources.scan_tools import ScanPorts, ScanObs, SingleScanPorts, SingleScanObs
from open_infra.utils.auth_permisson import AuthView
from open_infra.utils.common import assemble_api_result
from open_infra.utils.api_error_code import ErrCode
from django.conf import settings
from logging import getLogger

logger = getLogger("django")


class ScanPortView(AuthView):
    def get(self, request):
        """get all account"""
        scan_ports = ScanPorts()
        clouds_account = scan_ports.get_cloud_account()
        return clouds_account

    def post(self, request):
        """output a file"""
        dict_data = json.loads(request.body)
        user_name = AuthView.get_username(request)
        if dict_data.get("account") is None or not isinstance(dict_data["account"], list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        logger.info("ScanPortView collect:{}".format(dict_data["account"]))
        scan_ports = ScanPorts()
        is_handler = scan_ports.start_collect_thread(dict_data["account"], user_name)
        if not is_handler:
            err_code = ErrCode.STATUS_SUCCESS
        else:
            err_code = ErrCode.STATUS_SCAN_CLEAN
        return assemble_api_result(err_code)


class ScanPortProgressView(AuthView):
    "query download progress"

    def get(self, request):
        user_name = AuthView.get_username(request)
        scan_ports = ScanPorts()
        progress, data = scan_ports.query_progress(user_name)
        if progress == 0:
            return assemble_api_result(ErrCode.STATUS_SCAN_ING)
        elif progress == 1:
            res = HttpResponse(content=data, content_type="application/octet-stream")
            now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = settings.EXCEL_NAME.format(user_name, now_date)
            res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
            res['charset'] = 'utf-8'
            return res
        else:
            return assemble_api_result(ErrCode.STATUS_SCAN_FAILED)


class ScanObsView(AuthView):
    def get(self, request):
        """get all account"""
        scan_obs = ScanObs()
        clouds_account = scan_obs.get_cloud_account()
        return clouds_account

    def post(self, request):
        """output a file"""
        dict_data = json.loads(request.body)
        user_name = AuthView.get_username(request)
        if dict_data.get("account") is None or not isinstance(dict_data["account"], list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        logger.info("ScanObsView collect:{}".format(dict_data["account"]))
        scan_obs = ScanObs()
        is_handler = scan_obs.start_collect_thread(dict_data["account"], user_name)
        if not is_handler:
            err_code = ErrCode.STATUS_SUCCESS
        else:
            err_code = ErrCode.STATUS_SCAN_CLEAN
        return assemble_api_result(err_code)


class ScanObsProgressView(AuthView):
    "query download progress"

    def get(self, request):
        user_name = AuthView.get_username(request)
        scan_obs = ScanObs()
        progress, data = scan_obs.query_progress(user_name)
        if progress == 0:
            return assemble_api_result(ErrCode.STATUS_SCAN_ING)
        elif progress == 1:
            res = HttpResponse(content=data, content_type="application/octet-stream")
            now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = settings.SCAN_OBS_EXCEL_NAME.format(user_name, now_date)
            res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
            res['charset'] = 'utf-8'
            return res
        else:
            return assemble_api_result(ErrCode.STATUS_SCAN_FAILED)


# noinspection DuplicatedCode
class SingleScanPortView(AuthView):
    def get(self, request):
        user_name = AuthView.get_username(request)
        single_scan_ports = SingleScanPorts()
        progress, data = single_scan_ports.query_progress(user_name)
        if progress == 0:
            return assemble_api_result(ErrCode.STATUS_SCAN_ING)
        elif progress == 1:
            res = HttpResponse(content=data, content_type="application/octet-stream")
            now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = settings.EXCEL_NAME.format(user_name, now_date)
            res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
            res['charset'] = 'utf-8'
            return res
        else:
            return assemble_api_result(ErrCode.STATUS_SCAN_FAILED)

    def post(self, request):
        """output a file"""
        dict_data = json.loads(request.body)
        user_name = AuthView.get_username(request)
        ak = dict_data.get("ak")
        sk = dict_data.get("sk")
        zone = dict_data.get("zone")
        project_id = dict_data.get("project_id")
        logger.info("SingleScanPortView collect:{}".format(dict_data["account"]))
        single_scan_ports = SingleScanPorts()
        is_handler = single_scan_ports.start_collect_thread(ak, sk, user_name, zone, project_id)
        if not is_handler:
            err_code = ErrCode.STATUS_SUCCESS
        else:
            err_code = ErrCode.STATUS_SCAN_CLEAN
        return assemble_api_result(err_code)


# noinspection DuplicatedCode
class SingleScanObsView(AuthView):
    def get(self, request):
        user_name = AuthView.get_username(request)
        single_scan_obs = SingleScanObs()
        progress, data = single_scan_obs.query_progress(user_name)
        if progress == 0:
            return assemble_api_result(ErrCode.STATUS_SCAN_ING)
        elif progress == 1:
            res = HttpResponse(content=data, content_type="application/octet-stream")
            now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = settings.SCAN_OBS_EXCEL_NAME.format(user_name, now_date)
            res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
            res['charset'] = 'utf-8'
            return res
        else:
            return assemble_api_result(ErrCode.STATUS_SCAN_FAILED)

    def post(self, request):
        """output a file"""
        dict_data = json.loads(request.body)
        ak = dict_data.get("ak")
        sk = dict_data.get("sk")
        account = dict_data.get("account")
        user_name = AuthView.get_username(request)
        logger.info("ScanObsView collect:{}".format(account))
        single_scan_obs = SingleScanObs()
        is_handler = single_scan_obs.start_collect_thread(ak, sk, account, user_name)
        if not is_handler:
            err_code = ErrCode.STATUS_SUCCESS
        else:
            err_code = ErrCode.STATUS_SCAN_CLEAN
        return assemble_api_result(err_code)
