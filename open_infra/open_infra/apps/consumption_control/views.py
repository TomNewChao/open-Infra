
import threading

# Create your views here.
from datetime import datetime

from django.http import HttpResponse

from consumption_control.resources.bill_mgr import BillMgr
from consumption_control.resources.resource_utilization_mgr import ResourceUtilizationMgr
from open_infra.utils.api_error_code import ErrCode
from open_infra.utils.auth_permisson import AuthView
from open_infra.utils.common import list_param_check_and_trans, assemble_api_result

from logging import getLogger

logger = getLogger("django")


class BillView(AuthView):
    def get(self, request):
        dict_data = request.GET.dict()
        params_dict = list_param_check_and_trans(dict_data, order_by="bill_cycle")
        account = dict_data.get("account")
        resource_type = dict_data.get("type")
        if account:
            params_dict["account"] = account.strip()
        if resource_type:
            params_dict["resource_type"] = resource_type.strip()
        bill_mgr = BillMgr()
        data = bill_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class ResourceTypeNameView(AuthView):
    def get(self, request):
        bill_mgr = BillMgr()
        data = bill_mgr.get_all_resource_type_name()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class AccountNameView(AuthView):
    def get(self, request):
        bill_mgr = BillMgr()
        data = bill_mgr.get_all_account()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class YearAmountView(AuthView):
    def get(self, request):
        dict_data = request.GET.dict()
        if dict_data.get("year") is None:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            query_year = int(dict_data["year"])
        except ValueError:
            logger.error("[YearAmountView] invalid params:{}".format(dict_data["year"]))
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        bill_mgr = BillMgr()
        data = bill_mgr.get_year_amount(query_year)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class AllYearView(AuthView):
    def get(self, request):
        bill_mgr = BillMgr()
        data = bill_mgr.get_all_year()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class MonthAmountView(AuthView):
    _lock = threading.Lock()

    def get(self, request):
        dict_data = request.GET.dict()
        account = dict_data.get("account")
        bill_cycle = dict_data.get("bill_cycle")
        if account is None or bill_cycle is None:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        with MonthAmountView._lock:
            bill_mgr = BillMgr()
            bill_cycle_list = bill_cycle.split("-")
            if len(bill_cycle_list) != 2:
                return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
            if int(bill_cycle_list[1]) > 31 or int(bill_cycle_list[1]) < 0:
                return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
            data = bill_mgr.get_month_amount(account, bill_cycle)
            return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class AllBillCycleView(AuthView):
    def get(self, request):
        bill_mgr = BillMgr()
        data = bill_mgr.get_all_bill_cycle()
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class CPUResourceUtilizationMonth(AuthView):
    def get(self, request):
        resource_utilization_mgr = ResourceUtilizationMgr()
        return resource_utilization_mgr.get_cpu_month()


class CPUResourceUtilizationTable(AuthView):
    def get(self, request):
        date_str = request.GET.get("date")
        if date_str is None:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        resource_utilization_mgr = ResourceUtilizationMgr()
        data = resource_utilization_mgr.get_cpu_table_data(date_str)
        res = HttpResponse(content=data, content_type="application/octet-stream")
        now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = "cpu_resource_utilization_{}".format(now_date)
        res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
        res['charset'] = 'utf-8'
        return res


class CPUResourceUtilization(AuthView):
    def get(self, request):
        date_str = request.GET.get("date")
        if date_str is None:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        resource_utilization_mgr = ResourceUtilizationMgr()
        return resource_utilization_mgr.get_cpu_data(date_str)


class MemResourceUtilizationMonth(AuthView):
    def get(self, request):
        resource_utilization_mgr = ResourceUtilizationMgr()
        return resource_utilization_mgr.get_mem_month()


class MemResourceUtilizationTable(AuthView):
    def get(self, request):
        date_str = request.GET.get("date")
        if date_str is None:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        resource_utilization_mgr = ResourceUtilizationMgr()
        data = resource_utilization_mgr.get_mem_table_data(date_str)
        res = HttpResponse(content=data, content_type="application/octet-stream")
        now_date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = "mem_resource_utilization_{}".format(now_date)
        res["Content-Disposition"] = 'attachment;filename="{}"'.format(filename)
        res['charset'] = 'utf-8'
        return res


class MemResourceUtilization(AuthView):
    def get(self, request):
        date_str = request.GET.get("date")
        if date_str is None:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        resource_utilization_mgr = ResourceUtilizationMgr()
        return resource_utilization_mgr.get_mem_data(date_str)
