# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: urls.py
# @Software: PyCharm

from django.conf.urls import url
from obs_upload.views import ObsInteractView

urlpatterns = [
    # obs_interact is solve for using github to get config to upload file to obs
    # Detail: https://github.com/Open-Infra-Ops/obs-interact
    url(r'obs_interact', ObsInteractView.as_view()),

]
