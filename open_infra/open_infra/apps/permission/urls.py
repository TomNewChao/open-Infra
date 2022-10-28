# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm


from django.conf.urls import url
from permission.views import KubeConfigGitView, KubeConfigView, BatchKubeConfigView, ServiceInfoView

urlpatterns = [
    url(r'^github_pr', KubeConfigGitView.as_view()),
    url(r'^kubeconfig', KubeConfigView.as_view()),
    url(r'^batch_kubeconfig', BatchKubeConfigView.as_view()),
    url(r'^service_info', ServiceInfoView.as_view()),

]
