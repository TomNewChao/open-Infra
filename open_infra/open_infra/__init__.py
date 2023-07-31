# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: __init__.py
# @Software: PyCharm
import sys
import queue
import logging
from threading import Lock

from django.utils import asyncio

if sys.version > '3':
    try:
        # noinspection PyUnresolvedReferences
        import pymysql
        # noinspection PyUnresolvedReferences
        from pymysql import install_as_MySQLdb
        pymysql.version_info = (1, 4, 13, "final", 0)
        install_as_MySQLdb()
    except ImportError as e:
        logging.error('Import pymysql failed, please check this package, if not required please ignore it.')