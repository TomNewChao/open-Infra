# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm

from rest_framework.routers import DefaultRouter
from consumption_control.views import BillView, ResourceTypeNameView, AccountNameView, MonthAmountView, YearAmountView, \
    AllBillCycleView, AllYearView, CPUResourceUtilizationMonth, CPUResourceUtilization, CPUResourceUtilizationTable, \
    MemResourceUtilizationMonth, MemResourceUtilization, MemResourceUtilizationTable

urlpatterns = list()
router = DefaultRouter()
router.register("bill", BillView, basename="bill")
router.register("resource_type_name", ResourceTypeNameView, basename="resource_type_name")
router.register("account_name", AccountNameView, basename="account_name")
router.register("year_amount", YearAmountView, basename="year_amount")
router.register("all_year", AllYearView, basename="all_year")
router.register("month_amount", MonthAmountView, basename="month_amount")
router.register("all_bill_cycle", AllBillCycleView, basename="all_bill_cycle")
router.register("cpu_month", CPUResourceUtilizationMonth, basename="cpu_month")
router.register("cpu_data", CPUResourceUtilization, basename="cpu_data")
router.register("cpu_table", CPUResourceUtilizationTable, basename="cpu_table")
router.register("mem_month", MemResourceUtilizationMonth, basename="mem_month")
router.register("mem_data", MemResourceUtilization, basename="mem_data")
router.register("mem_table", MemResourceUtilizationTable, basename="mem_table")
urlpatterns += router.urls
