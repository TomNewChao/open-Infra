# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm

from rest_framework.routers import DefaultRouter

from app_tools.views import ScanPortView, ScanObsView, SingleScanPortView, SingleScanObsView, PortsListView, \
    PortsListDeleteView

urlpatterns = list()
router = DefaultRouter()
router.register("high_risk_port", PortsListView, basename="high_risk_port")
router.register("bulk_high_risk_port", PortsListDeleteView, basename="bulk_high_risk_port")
router.register("scan_port", ScanPortView, basename="scan_port")
router.register("single_scan_port", SingleScanPortView, basename="single_scan_port")
router.register("single_scan_port_progress", SingleScanPortView, basename="single_scan_port_progress")
router.register("single_scan_obs", SingleScanObsView, basename="single_scan_obs")
router.register("single_scan_obs_progress", SingleScanObsView, basename="single_scan_obs_progress")
urlpatterns += router.urls
