# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm

from django.conf.urls import url
from clouds_tools.views import ScanPortView, ScanObsView, SingleScanPortView, SingleScanObsView, PortsListView, EipView, \
    PortsListDeleteView, ServiceView, SlaExportView, ObsInteractView, NameSpaceView, ClusterView, AccountView, BillView, \
    ResourceTypeNameView, AccountNameView, MonthAmountView, YearAmountView, AllBillCycleView, IndexView, AllYearView, \
    CPUResourceUtilization, CPUResourceUtilizationMonth, MemResourceUtilizationMonth, MemResourceUtilization

urlpatterns = [
    # query/create/delete high level port
    url(r'^high_risk_port$', PortsListView.as_view()),
    url(r'^bulk_high_risk_port$', PortsListDeleteView.as_view()),
    url(r'^scan_port$', ScanPortView.as_view()),
    url(r'^single_scan_port$', SingleScanPortView.as_view()),
    url(r'^single_scan_port/progress$', SingleScanPortView.as_view()),

    # scan obs anonymous bucket
    url(r'^scan_obs$', ScanObsView.as_view()),
    url(r'^single_scan_obs$', SingleScanObsView.as_view()),
    url(r'^single_scan_obs/progress$', SingleScanObsView.as_view()),

    #  query eip
    url(r'^eip$', EipView.as_view()),

    #  query cla
    url(r'^service$', ServiceView.as_view()),
    url(r'^namespace$', NameSpaceView.as_view()),
    url(r'^cluster$', ClusterView.as_view()),
    url(r'^sla_export$', SlaExportView.as_view()),

    # obs_interact is solve for using github to get config to upload file to obs
    # Detail: https://github.com/Open-Infra-Ops/obs-interact
    url(r'obs_interact', ObsInteractView.as_view()),

    # account
    url(r'account$', AccountView.as_view()),

    # bill
    url(r'bill$', BillView.as_view()),
    url(r'resource_type_name', ResourceTypeNameView.as_view()),
    url(r'account_name', AccountNameView.as_view()),
    url(r'year_amount', YearAmountView.as_view()),
    url(r'all_year', AllYearView.as_view()),
    url(r'month_amount', MonthAmountView.as_view()),
    url(r'all_bill_cycle', AllBillCycleView.as_view()),

    # index
    url(r'index$', IndexView.as_view()),

    # resource utilization
    url("cpu_month", CPUResourceUtilizationMonth.as_view()),
    url("cpu_data", CPUResourceUtilization.as_view()),

    url("mem_month", MemResourceUtilizationMonth.as_view()),
    url("mem_data", MemResourceUtilization.as_view()),




]
