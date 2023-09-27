# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm


from rest_framework.routers import DefaultRouter

from permission.views import KubeConfigGitView, KubeConfigView, BatchKubeConfigView

urlpatterns = list()
router = DefaultRouter()
router.register("kubeconfig_webhook", KubeConfigGitView, basename="bill")
router.register("kubeconfig", KubeConfigView, basename="resource_type_name")
router.register("batch_kubeconfig", BatchKubeConfigView, basename="batch_kubeconfig")

urlpatterns += router.urls
