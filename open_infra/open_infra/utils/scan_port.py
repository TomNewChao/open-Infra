# -*- coding: utf-8 -*-
# @Time    : 2022/7/7 10:30
# @Author  : Tom_zc
# @FileName: scan_port.py
# @Software: PyCharm
import os
import re
import shutil

import requests
import subprocess
import uuid
from abc import abstractmethod
from open_infra.utils.common import func_retry
from collections import defaultdict
from logging import getLogger
from django.conf import settings

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkcore.client import Client
from huaweicloudsdkeip.v2 import EipClient as EipClientV2
from huaweicloudsdkeip.v2 import ListPublicipsRequest as ListPublicipsRequestV2
from huaweicloudsdkeip.v3 import EipClient as EipClientV3
from huaweicloudsdkeip.v3 import ListPublicipsRequest as ListPublicipsRequestV3

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = getLogger("django")


class GlobalConfig(object):
    eip_v2_zone = ["cn-south-4", ]
    ip_result_name = "ip_result.txt"
    tcp_search_cmd = "nmap -sS -Pn -n --open --min-hostgroup 4 --min-parallelism 1024 --host-timeout 180 -T4 -v -oG {} {}"
    udp_search_cmd = "nmap -sU --min-hostgroup 4 --min-parallelism 1024 --host-timeout 180 -v -oG {} {}"


# noinspection DuplicatedCode
class EndPoint(object):
    vpc_endpoint = "https://vpc.{}.myhuaweicloud.com"
    nat_endpoint = "https://nat.{}.myhuaweicloud.com"
    elb_endpoint = "https://elb.{}.myhuaweicloud.com"
    bms_endpoint = "https://bms.{}.myhuaweicloud.com"
    ecs_endpoint = "https://ecs.{}.myhuaweicloud.com"
    rds_endpoint = "https://rds.{}.myhuaweicloud.com"


# noinspection PyUnresolvedReferences
class BaseInstance(object):
    def __init__(self, base_client, config, credentials, endpoint):
        if not issubclass(base_client, Client):
            raise Exception("base client must be client")
        self.base_client = base_client.new_builder() \
            .with_http_config(config) \
            .with_credentials(credentials) \
            .with_endpoint(endpoint) \
            .build()

    @abstractmethod
    def set_req_method(self):
        pass

    @abstractmethod
    def parse_response_data(self, response_dict):
        pass

    def show_infos(self, *args, **kwargs):
        info_request, method = self.set_req_method()
        show_infos_req = info_request(*args, **kwargs)
        show_infos_method = getattr(self.base_client, method)
        ret = show_infos_method(show_infos_req)
        return ret.to_dict()


class EipInstanceV2(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(EipInstanceV2, self).__init__(*args, **kwargs)

    def set_req_method(self):
        return ListPublicipsRequestV2, "list_publicips"

    def parse_response_data(self, response_dict):
        return response_dict['publicips']


class EipInstanceV3(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(EipInstanceV3, self).__init__(*args, **kwargs)

    def set_req_method(self):
        return ListPublicipsRequestV3, "list_publicips"

    def parse_response_data(self, response_dict):
        return response_dict['publicips']


# noinspection DuplicatedCode
class EipTools(object):
    def __init__(self, *args, **kwargs):
        super(EipTools, self).__init__(*args, **kwargs)

    @classmethod
    def get_eip_config(cls):
        config = HttpConfig.get_default_config()
        config.ignore_ssl_verification = True
        return config

    @classmethod
    def read_txt(cls, file_path):
        with open(file_path, "r") as f:
            return f.readlines()

    # noinspection PyUnresolvedReferences
    @classmethod
    def parse_tcp_result_txt_all(cls, tcp_content_list):
        host_data = defaultdict(list)
        for info in tcp_content_list:
            if "Host:" in info and "Ports:":
                ret_list = list()
                info_list = info.split("Ports:")
                ip = re.match(r"Host: (.*?)\(\)", info_list[0])
                if not ip:
                    continue
                ip = ip.groups()[0].strip()
                infor_str_list = info_list[1].split()
                for infor_str_temp in infor_str_list:
                    if "/" in infor_str_temp:
                        for infor_str_temp_data in infor_str_temp.split(","):
                            port = re.match(r"(.*?)///", infor_str_temp_data.strip())
                            if not port:
                                continue
                            ret_list.append(port.groups()[0].strip())
                host_data[ip] = ret_list
        return host_data

    @classmethod
    def parse_tcp_result_txt(cls, tcp_content_list):
        ret_list = list()
        for info in tcp_content_list:
            if "Host:" in info and "Ports:" in info:
                info_list = info.split("Ports:")
                logger.info(info_list)
                infor_str_list = info_list[1].split()
                for infor_str_temp in infor_str_list:
                    if "/" in infor_str_temp:
                        for infor_str_temp_data in infor_str_temp.split(","):
                            port = re.match(r"(.*?)///", infor_str_temp_data.strip())
                            if not port:
                                continue
                            port_str = port.groups()[0].strip()
                            port_content = list(filter(lambda x: x != "", port_str.split('/')))
                            if settings.HIGH_RISK_PORT and int(port_content[0]) not in settings.HIGH_RISK_PORT:
                                continue
                            ret_list.append(port_content)
        return ret_list

    @classmethod
    def get_device_info(cls, instance_list):
        ret_dict = dict()
        for instance_temp in instance_list:
            instance_info = instance_temp.show_infos()
            device_info = instance_temp.parse_response_data(instance_info)
            for key, value in device_info.items():
                if key not in ret_dict.keys():
                    ret_dict[key] = value
        return ret_dict

    def get_data_list(self, project_id, zone, ak, sk):
        config = self.get_eip_config()
        credentials = BasicCredentials(ak, sk, project_id)
        if zone in GlobalConfig.eip_v2_zone:
            eip_instance = EipInstanceV2(EipClientV2, config, credentials, EndPoint.vpc_endpoint.format(zone))
        else:
            eip_instance = EipInstanceV3(EipClientV3, config, credentials, EndPoint.vpc_endpoint.format(zone))
        eip_dict = eip_instance.show_infos()
        eip_list = eip_instance.parse_response_data(eip_dict)
        eip_ip_list = list()
        for eip_info in eip_list:
            eip_ip_list.append(eip_info['public_ip_address'])
        return eip_ip_list

    @func_retry(tries=1)
    def get_single_data_list(self, project_id, zone, ak, sk):
        config = self.get_eip_config()
        credentials = BasicCredentials(ak, sk, project_id)
        if zone in GlobalConfig.eip_v2_zone:
            eip_instance = EipInstanceV2(EipClientV2, config, credentials, EndPoint.vpc_endpoint.format(zone))
        else:
            eip_instance = EipInstanceV3(EipClientV3, config, credentials, EndPoint.vpc_endpoint.format(zone))
        eip_dict = eip_instance.show_infos()
        eip_list = eip_instance.parse_response_data(eip_dict)
        eip_ip_list = list()
        for eip_info in eip_list:
            eip_ip_list.append(eip_info['public_ip_address'])
        return eip_ip_list

    @classmethod
    def execute_cmd(cls, cmd):
        """
        Execute commands through subprocess
        :param cmd: string, the cmd
        :return: string, the result of execute cmd
        """
        return subprocess.getstatusoutput(cmd)

    @classmethod
    def request_server(cls, ip, ports):
        url = r"http://{}:{}/".format(ip, ports)
        try:
            ret = requests.get(url, timeout=(180, 180))
            server_info = ret.headers.get("Server", "Unknown")
        except Exception as e:
            logger.info("collect url:{}, err:{}".format(url, e))
            server_info = str(e)
        return server_info

    @classmethod
    def collect_tcp_server_info(cls, tcp_ret_dict):
        server_dict = defaultdict(list)
        for ip, ip_info in tcp_ret_dict.items():
            for ip_temp in ip_info:
                server_info = cls.request_server(ip, ip_temp[0])
                server_dict[ip].append([ip_temp[0], server_info])
        return server_dict


# noinspection DuplicatedCode
def scan_port(username, config_list):
    eip_tools = EipTools()
    tcp_ret_dict, udp_ret_dict, tcp_server_info = dict(), dict(), dict()
    logger.info("############1.start to collect ip######")
    result_list = list()
    for config_item in config_list:
        ak = config_item["ak"]
        sk = config_item["sk"]
        project_info = config_item["project_info"]
        for project_temp in project_info:
            logger.info("Collect the zone of info:{}".format(project_temp["zone"]))
            project_id = project_temp["project_id"]
            zone = project_temp["zone"]
            ret_temp = eip_tools.get_data_list(project_id, zone, ak, sk)
            result_list.extend(ret_temp or [])
    result_list = list(set(result_list))
    if not result_list:
        return tcp_ret_dict, udp_ret_dict, tcp_server_info
    logger.info("###########2.lookup port###################")
    if not username:
        username = "anonymous_{}".format(uuid.uuid1())
    ip_result_dir = os.path.join(settings.LIB_PATH, "scan_port_{}".format(username))
    if not os.path.exists(ip_result_dir):
        os.mkdir(ip_result_dir)
    temp_name = os.path.join(ip_result_dir, GlobalConfig.ip_result_name)
    for ip in result_list:
        logger.info("1.start to collect tcp:{} info".format(ip))
        ret_code, data = eip_tools.execute_cmd(GlobalConfig.tcp_search_cmd.format(temp_name, ip))
        if ret_code != 0:
            logger.error("search tcp:{}, error:{}".format(ip, data))
        else:
            tcp_content_list = eip_tools.read_txt(temp_name)
            tcp_ret_dict[ip] = eip_tools.parse_tcp_result_txt(tcp_content_list)
        logger.info("2.start to collect udp:{} info".format(ip))
        ret_code, data = eip_tools.execute_cmd(GlobalConfig.udp_search_cmd.format(temp_name, ip))
        if ret_code != 0:
            logger.error("search tcp:{}, error:{}".format(ip, data))
        else:
            udp_content_list = eip_tools.read_txt(temp_name)
            udp_ret_dict[ip] = eip_tools.parse_tcp_result_txt(udp_content_list)
    shutil.rmtree(ip_result_dir)
    logger.info("###########3.lookup service info###################")
    tcp_server_info = EipTools.collect_tcp_server_info(tcp_ret_dict)
    logger.info("###########4.return tar file###################")
    return tcp_ret_dict, udp_ret_dict, tcp_server_info


# noinspection DuplicatedCode
def single_scan_port(ak, sk, zone, project_id, username=None):
    eip_tools = EipTools()
    tcp_ret_dict, udp_ret_dict, tcp_server_info = dict(), dict(), dict()
    ret_temp = eip_tools.get_single_data_list(project_id, zone, ak, sk)
    if ret_temp is None:
        logger.info("single_scan_port: There is get eip:{}".format(ret_temp))
        return tcp_ret_dict, udp_ret_dict, tcp_server_info
    result_list = list(set(ret_temp))
    if not result_list:
        logger.info("single_scan_port: There is no ip:{}".format(zone))
        return tcp_ret_dict, udp_ret_dict, tcp_server_info
    if not username:
        username = "anonymous_{}".format(uuid.uuid1())
    ip_result_dir = os.path.join(settings.LIB_PATH, "scan_port_{}".format(username))
    if not os.path.exists(ip_result_dir):
        os.mkdir(ip_result_dir)
    temp_name = os.path.join(ip_result_dir, GlobalConfig.ip_result_name)
    logger.info("single_scan_port collect ips:{}".format(result_list))
    for ip in result_list:
        logger.info("1.start to collect tcp:{} info".format(ip))
        ret_code, data = eip_tools.execute_cmd(GlobalConfig.tcp_search_cmd.format(temp_name, ip))
        if ret_code != 0:
            logger.error("search tcp:{}, error:{}".format(ip, data))
        else:
            tcp_content_list = eip_tools.read_txt(temp_name)
            tcp_ret_dict[ip] = eip_tools.parse_tcp_result_txt(tcp_content_list)
        logger.info("2.start to collect udp:{} info".format(ip))
        ret_code, data = eip_tools.execute_cmd(GlobalConfig.udp_search_cmd.format(temp_name, ip))
        if ret_code != 0:
            logger.error("search tcp:{}, error:{}".format(ip, data))
        else:
            udp_content_list = eip_tools.read_txt(temp_name)
            udp_ret_dict[ip] = eip_tools.parse_tcp_result_txt(udp_content_list)
    shutil.rmtree(ip_result_dir)
    tcp_server_info = EipTools.collect_tcp_server_info(tcp_ret_dict)
    logger.info("2.return dict file:{}, {}, {}".format(tcp_ret_dict, udp_ret_dict, tcp_server_info))
    return tcp_ret_dict, udp_ret_dict, tcp_server_info
