# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 14:08
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm


from django.conf.urls import url
from app_resources.views import ServiceView, SlaExportView, ClusterView, AccountView, DetailServiceView, EipView, IndexView, RegionView, RepoView

urlpatterns = [
    # index
    url(r'^index$', IndexView.as_view()),

    # query account
    url(r'^account$', AccountView.as_view()),

    # query eip
    url(r'^eip$', EipView.as_view()),

    # query service and sla
    url(r'^service$', ServiceView.as_view()),
    url(r'^detail_service$', DetailServiceView.as_view()),
    url(r'^cluster$', ClusterView.as_view()),
    url(r'^region$', RegionView.as_view()),
    url(r'^sla_export$', SlaExportView.as_view()),

    # cve interface
    url(r'^repo$', RepoView.as_view()),

]
