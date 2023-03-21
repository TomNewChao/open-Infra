# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm

from django.conf.urls import url
from consumption_control.views import BillView, ResourceTypeNameView, AccountNameView, MonthAmountView, YearAmountView, \
    AllBillCycleView, AllYearView, CPUResourceUtilizationMonth, CPUResourceUtilization, CPUResourceUtilizationTable, \
    MemResourceUtilizationMonth, MemResourceUtilization, MemResourceUtilizationTable

urlpatterns = [
    # bill
    url(r'^bill$', BillView.as_view()),
    url(r'^resource_type_name$', ResourceTypeNameView.as_view()),
    url(r'^account_name$', AccountNameView.as_view()),
    url(r'^year_amount$', YearAmountView.as_view()),
    url(r'^all_year$', AllYearView.as_view()),
    url(r'^month_amount$', MonthAmountView.as_view()),
    url(r'^all_bill_cycle$', AllBillCycleView.as_view()),

    # resource utilization
    url("^cpu_month$", CPUResourceUtilizationMonth.as_view()),
    url("^cpu_data$", CPUResourceUtilization.as_view()),
    url("^cpu_table$", CPUResourceUtilizationTable.as_view()),

    url("^mem_month$", MemResourceUtilizationMonth.as_view()),
    url("^mem_data$", MemResourceUtilization.as_view()),
    url("^mem_table$", MemResourceUtilizationTable.as_view()),

]
