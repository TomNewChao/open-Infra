# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm

from django.conf.urls import url
from clouds_tools.views import ScanPortView, ScanObsView, SingleScanPortView, SingleScanObsView, PortsListView, \
    PortsListDeleteView

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

]
