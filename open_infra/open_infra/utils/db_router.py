#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19-6-10 下午10:26
# @Author  : Tom
# @Site    : 
# @File    : db_router.py
# @Software: PyCharm


class MasterSlaveDBRouter(object):
    """数据库读写路由"""

    def db_for_read(self, model, **hints):
        """读"""
        return "slave"

    def db_for_write(self, model, **hints):
        """写"""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """是否运行关联操作"""
        return True