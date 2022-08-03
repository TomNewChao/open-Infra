# -*- coding: utf-8 -*-
# @Time    : 2022/8/2 20:44
# @Author  : Tom_zc
# @FileName: default_port_list.py
# @Software: PyCharm
import copy


class HighRiskPort(object):
    default_port_list = {
        21: "FTP", 22: "SSH", 23: "telnet", 69: "Tftp", 135: "rpc", 137: "netbios", 138: "netbios", 139: "netbios",
        161: "snmap", 177: "Xmanager/Xwin", 389: "ldap", 445: "smb", 513: "Rlogin", 873: "rsync", 1025: "RPC",
        1099: "java", 1433: "mssql", 1521: "oracle", 2082: "cpanel主机管理系统登陆", 2083: "cpanel主机管理系统登陆",
        2222: "DA虚拟主机管理系统登陆", 2601: "zebra路由器", 2604: "zebra路由器", 3128: "squid代理默认端口", 3306: "mysql",
        3312: "kangle主机管理系统登陆", 3311: "kangle主机管理系统登陆", 3389: "RDP", 4440: "rundeck", 4848: "GlassFish",
        4899: "Remoteadmin", 5432: "postgres", 6379: "redis", 7001: "weblogic", 7002: "weblogic", 7778: "Kloxo主机控制面板登录",
        8080: "tomcat\jboss", 8649: "ganglia", 8083: "Vestacp主机管理系统", 9000: "fcgi", 9200: "elasticsearch",
        9043: "websphere", 10000: "Virtualmin/Webmin", 27017: "mongodb", 50060: "hadoop", 50030: "hadoop"
    }
    _mem_port_list = None

    @classmethod
    def get_port_dict(cls):
        if cls._mem_port_list is None:
            mem_port_list = copy.deepcopy(cls.default_port_list)
            for i in range(6000, 6064):
                mem_port_list[i] = "x11"
            for i in range(50000, 50051):
                mem_port_list[i] = "db2"
            cls._mem_port_list = dict(sorted(mem_port_list.items()))
        return cls._mem_port_list
