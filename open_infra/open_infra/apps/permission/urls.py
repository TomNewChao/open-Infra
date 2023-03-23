# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm


from django.conf.urls import url
from permission.views import KubeConfigGitView, KubeConfigView, BatchKubeConfigView

urlpatterns = [
    # the webhook github api of kubeconfig-interact
    url(r'^kubeconfig_webhook', KubeConfigGitView.as_view()),

    # get the detail of kubeconfig and modify kubeconfig
    url(r'^kubeconfig', KubeConfigView.as_view()),

    # get the list of kubeconfig and batch delete kubeconfig
    url(r'^batch_kubeconfig', BatchKubeConfigView.as_view()),

]
