#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-5-22 下午9:28
# @Author  : Tom
# @Site    : 
# @File    : login.py.py
# @Software: PyCharm


from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    """
    在扩展累中写as_view方法，将返回的数据进行装饰
    """

    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return login_required(view)
