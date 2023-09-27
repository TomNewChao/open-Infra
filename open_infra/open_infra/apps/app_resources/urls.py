# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 14:08
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm

from rest_framework.routers import DefaultRouter

from app_resources.views import ServiceView, SlaExportView, ClusterView, AccountView, DetailServiceView, EipView, \
    IndexView, RegionView, RepoView, BaseOsView, BaseImageView, CommunityView, SeviceExportView, ServiceIntroduceView

urlpatterns = list()
router = DefaultRouter()
router.register("index", IndexView, basename="index")
router.register("account", AccountView, basename="account")
router.register("eip", EipView, basename="eip")
router.register("service", ServiceView, basename="service")
router.register("detail_service", DetailServiceView, basename="detail_service")
router.register("service_export", SeviceExportView, basename="service_export")
router.register("cluster", ClusterView, basename="cluster")
router.register("region", RegionView, basename="region")
router.register("community", CommunityView, basename="community")
router.register("base_os", BaseOsView, basename="base_os")
router.register("base_image", BaseImageView, basename="base_image")
router.register("sla_export", SlaExportView, basename="sla_export")
router.register("service_introduce", ServiceIntroduceView, basename="service_introduce")
router.register("repo", RepoView, basename="repo")
urlpatterns += router.urls
