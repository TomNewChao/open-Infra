# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 8:44
# @Author  : Tom_zc
# @FileName: __init__.py
# @Software: PyCharm
import random
import sys
import logging
from django.utils import asyncio

if sys.version > '3':
    try:
        import pymysql
        from pymysql import install_as_MySQLdb
        pymysql.version_info = (1, 4, 13, "final", 0)
        install_as_MySQLdb()
    except ImportError as e:
        logging.error('Import pymysql failed, please check this package, if not required please ignore it.')

from django.db.backends.mysql.base import CursorWrapper, DatabaseWrapper
from django.core.exceptions import ImproperlyConfigured

try:
    import MySQLdb as Database
except ImportError as err:
    raise ImproperlyConfigured(
        'Error loading MySQLdb module.\n'
        'Did you install mysqlclient?'
    ) from err


class ConnectPool(object):
    def __init__(self, conn_params, pool_size):
        self.conn_params = conn_params
        self.pool_size = pool_size
        self.connects = []

    @staticmethod
    def instance(conn_params, pool_size):
        if not hasattr(ConnectPool, '_instance'):
            ConnectPool._instance = ConnectPool(conn_params, pool_size)
        return ConnectPool._instance

    def new_connect(self):
        new_connect = Database.connect(**self.conn_params)
        if new_connect.encoders.get(bytes) is bytes:
            new_connect.encoders.pop(bytes)
        return new_connect

    def get_connection(self):
        if len(self.connects) < self.pool_size:
            # 1.make new connect
            new_connect = self.new_connect()
            # 2.add connect into list
            self.connects.append(new_connect)
            # 3. return the current connect
            return new_connect
        index = random.randint(0, self.pool_size - 1)
        try:
            # 1.choice a connect
            new_connect = self.connects[index]
            # 2.ping, if not ok, and new a connect
            new_connect.ping()
        except Exception as e:
            logging.error("Mysql connection has expired, reconnecting:{}".format(e))
            new_connect = self.new_connect()
            self.connects[index] = new_connect
        return new_connect


def create_cursor(self, name=None):
    # Solve the connection failure error, check the validity of the connection, if otherwise recycle and recreate
    self.connection.ping(reconnect=True)
    cursor = self.connection.cursor()
    return CursorWrapper(cursor)


def get_new_connection(self, conn_params):
    """get the connection"""
    pool_size = self.settings_dict.get('POOL_SIZE') or 1
    return ConnectPool.instance(conn_params, pool_size).get_connection()


DatabaseWrapper.create_cursor = asyncio.async_unsafe(create_cursor)
DatabaseWrapper.get_new_connection = asyncio.async_unsafe(get_new_connection)
