import json
from datetime import datetime
from django.http import HttpResponse
from clouds_tools.resources.scan_tools import ScanPortsMgr, ScanObsMgr, SingleScanPortsMgr, SingleScanObsMgr, EipMgr
from open_infra.utils.auth_permisson import AuthView
from open_infra.utils.common import assemble_api_result, list_param_check_and_trans
from open_infra.utils.api_error_code import ErrCode
from django.conf import settings
from logging import getLogger
from open_infra.utils.default_port_list import HighRiskPort

logger = getLogger("django")


class ScanPortView(AuthView):
    def get(self, request):
        """get all account"""
        scan_ports = ScanPortsMgr()
        clouds_account = scan_ports.get_cloud_account()
        return clouds_account

    def post(self, request):
        """output a file"""
        dict_data = json.loads(request.body)
        if dict_data.get("account") is None or not isinstance(dict_data["account"], list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        logger.info("ScanPortView collect:{}".format(dict_data["account"]))
        scan_ports = ScanPortsMgr()
        content = scan_ports.query_data(dict_data["account"])
        res = HttpResponse(content=content, content_type="application/octet-stream")
        now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = settings.EXCEL_NAME.format(now_date)
        res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
        res['charset'] = 'utf-8'
        return res


class ScanObsView(AuthView):
    def get(self, request):
        """get all account"""
        scan_obs = ScanObsMgr()
        clouds_account = scan_obs.get_cloud_account()
        return clouds_account

    def post(self, request):
        """output a file"""
        dict_data = json.loads(request.body)
        if dict_data.get("account") is None or not isinstance(dict_data["account"], list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        logger.info("ScanObsView collect:{}".format(dict_data["account"]))
        scan_obs = ScanObsMgr()
        data = scan_obs.query_data(dict_data["account"])
        res = HttpResponse(content=data, content_type="application/octet-stream")
        now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = settings.SCAN_OBS_EXCEL_NAME.format(now_date)
        res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
        res['charset'] = 'utf-8'
        return res


class SingleScanPortView(AuthView):

    def post(self, request):
        """output a file"""
        dict_data = json.loads(request.body)
        ak = dict_data.get("ak").strip()
        sk = dict_data.get("sk").strip()
        single_scan_ports = SingleScanPortsMgr()
        result = single_scan_ports.start_collect_thread(ak, sk)
        if result:
            return assemble_api_result(ErrCode.STATUS_SUCCESS)
        else:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)


class SingleScanPortProgressView(AuthView):
    def post(self, request):
        dict_data = json.loads(request.body)
        ak = dict_data.get("ak").strip()
        sk = dict_data.get("sk").strip()
        single_scan_ports = SingleScanPortsMgr()
        progress, data = single_scan_ports.query_progress(ak, sk)
        res = HttpResponse(content=data, content_type="application/octet-stream")
        if progress == 1:
            now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = settings.EXCEL_NAME.format(now_date)
            res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
            res['charset'] = 'utf-8'
            return res
        else:
            return assemble_api_result(ErrCode.STATUS_SCAN_ING)


# noinspection DuplicatedCode
class SingleScanObsView(AuthView):

    def post(self, request):
        """output a file"""
        dict_data = json.loads(request.body)
        ak = dict_data.get("ak").strip()
        sk = dict_data.get("sk").strip()
        account = dict_data.get("account").strip()
        logger.info("ScanObsView collect:{}".format(account))
        single_scan_obs = SingleScanObsMgr()
        result = single_scan_obs.start_collect_thread(ak, sk, account)
        if result:
            return assemble_api_result(ErrCode.STATUS_SUCCESS)
        else:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)


class SingleScanObsProgressView(AuthView):
    def post(self, request):
        dict_data = json.loads(request.body)
        ak = dict_data.get("ak").strip()
        sk = dict_data.get("sk").strip()
        account = dict_data.get("account").strip()
        single_scan_obs = SingleScanObsMgr()
        progress, data = single_scan_obs.query_progress(ak, sk, account)
        if progress == 0:
            return assemble_api_result(ErrCode.STATUS_SCAN_ING)
        elif progress == 1:
            res = HttpResponse(content=data, content_type="application/octet-stream")
            now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            filename = settings.SCAN_OBS_EXCEL_NAME.format(now_date)
            res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
            res['charset'] = 'utf-8'
            return res
        else:
            return assemble_api_result(ErrCode.STATUS_SCAN_FAILED)


class PortsListView(AuthView):
    def get(self, request):
        port_dict = HighRiskPort.get_port_dict()
        ret_list = list()
        for port_info, port_describe in port_dict.items():
            ret_list.append({
                "port": port_info,
                "describe": port_describe
            })
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=ret_list)


class EipView(AuthView):
    def get(self, request):
        params_dict = list_param_check_and_trans(request.GET.dict())
        eip_mgr = EipMgr()
        data = eip_mgr.list_eip(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)
