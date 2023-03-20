# -*- coding: utf-8 -*-
# @Time    : 2023/3/10 14:42
# @Author  : Tom_zc
# @FileName: admin.py
# @Software: PyCharm
from django.contrib import admin

admin.site.site_title = "open-infra"
admin.site.site_header = "open-infra后台管理"


class BaseAdmin(admin.ModelAdmin):
    pass
