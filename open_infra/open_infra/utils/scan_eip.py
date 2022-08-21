# -*- coding: utf-8 -*-
# @Time    : 2022/6/8 17:30
# @Author  : Tom_zc
# @FileName: scan_eip.py
# @Software: PyCharm


import requests
import logging

from abc import abstractmethod

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkcore.client import Client
from huaweicloudsdkeip.v2 import EipClient as EipClientV2
from huaweicloudsdkeip.v2 import ListPublicipsRequest as ListPublicIpsRequestV2
from huaweicloudsdkeip.v3 import EipClient as EipClientV3
from huaweicloudsdkeip.v3 import ListPublicipsRequest as ListPublicIpsRequestV3
from huaweicloudsdknat.v2 import NatClient, ListNatGatewaysRequest
from huaweicloudsdkelb.v2 import ElbClient, ListLoadbalancersRequest
from huaweicloudsdkbms.v1 import BmsClient, ListBareMetalServersRequest
from huaweicloudsdkecs.v2 import EcsClient, NovaListServersDetailsRequest
from huaweicloudsdkrds.v3 import RdsClient, ListInstancesRequest
from huaweicloudsdkcore.exceptions.exceptions import ClientRequestException, ConnectionException


from clouds_tools.resources.constants import HWCloudEipStatus, HWCloudEipType
from open_infra.utils.common import func_retry
from django.conf import settings

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logger = logging.getLogger("django")


# noinspection DuplicatedCode
class EndPoint(object):
    vpc_endpoint = "https://vpc.{}.myhuaweicloud.com"
    nat_endpoint = "https://nat.{}.myhuaweicloud.com"
    elb_endpoint = "https://elb.{}.myhuaweicloud.com"
    bms_endpoint = "https://bms.{}.myhuaweicloud.com"
    ecs_endpoint = "https://ecs.{}.myhuaweicloud.com"
    rds_endpoint = "https://rds.{}.myhuaweicloud.com"


# noinspection PyUnresolvedReferences,DuplicatedCode
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

    def parse_response_data(self, response_dict):
        dict_data = dict()
        for item in response_dict[self.ret_filed]:
            dict_data[item["id"]] = {
                "name": item["name"],
                "instance_type": self.instance_name
            }
        return dict_data

    def show_infos(self, *args, **kwargs):
        info_request, method = self.set_req_method()
        show_infos_req = info_request(*args, **kwargs)
        try:
            show_infos_method = getattr(self.base_client, method)
            ret = show_infos_method(show_infos_req)
            return ret.to_dict()
        except ClientRequestException as e:
            logger.error("show_infos ClientRequestException:{}".format(e))
            return dict()
        except ConnectionException as e:
            logger.error("show_infos ConnectionException:{}".format(e))
            if e.err_message.endswith("Name or service not known"):
                return dict()
            else:
                raise Exception(e)


class EipInstanceV2(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(EipInstanceV2, self).__init__(*args, **kwargs)

    def set_req_method(self):
        return ListPublicIpsRequestV2, "list_publicips"

    def parse_response_data(self, response_dict):
        return response_dict['publicips']


class EipInstanceV3(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(EipInstanceV3, self).__init__(*args, **kwargs)

    def set_req_method(self):
        return ListPublicIpsRequestV3, "list_publicips"

    def parse_response_data(self, response_dict):
        return response_dict['publicips']


class NatInstance(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(NatInstance, self).__init__(*args, **kwargs)
        self.instance_name = "NAT网关"
        self.ret_filed = "nat_gateways"

    def set_req_method(self):
        return ListNatGatewaysRequest, "list_nat_gateways"


class LoadBalanceInstance(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(LoadBalanceInstance, self).__init__(*args, **kwargs)
        self.instance_name = "负载均衡器"
        self.ret_filed = "loadbalancers"

    def set_req_method(self):
        return ListLoadbalancersRequest, "list_loadbalancers"


class BMSInstance(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(BMSInstance, self).__init__(*args, **kwargs)
        self.instance_name = "裸金属服务器"
        self.ret_filed = "servers"

    def set_req_method(self):
        return ListBareMetalServersRequest, "list_bare_metal_servers"


class EcsInstance(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(EcsInstance, self).__init__(*args, **kwargs)
        self.instance_name = "云服务器"
        self.ret_filed = "servers"

    def set_req_method(self):
        return NovaListServersDetailsRequest, "nova_list_servers_details"


class RdsInstance(BaseInstance):
    def __init__(self, *args, **kwargs):
        super(RdsInstance, self).__init__(*args, **kwargs)
        self.instance_name = "云数据库 RDS"
        self.ret_filed = "instances"

    def set_req_method(self):
        return ListInstancesRequest, "list_instances"


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
    def get_device_info(cls, instance_list):
        ret_dict = dict()
        for instance_temp in instance_list:
            instance_info = instance_temp.show_infos()
            if not instance_info:
                continue
            device_info = instance_temp.parse_response_data(instance_info)
            for key, value in device_info.items():
                if key not in ret_dict.keys():
                    ret_dict[key] = value
        return ret_dict

    @classmethod
    def parse_ips_v2(cls, eip_list, zone):
        result_list = list()
        zone_alias = settings.ZONE_ALIAS_DICT.get(zone, zone)
        for eip_info in eip_list:
            temp = list()
            temp.append(eip_info['public_ip_address'])
            temp.append(eip_info['public_ipv6_address'])
            temp.append(eip_info['id'])
            eip_status = HWCloudEipStatus.__dict__.get(eip_info['status'], " ")
            temp.append(eip_status[0])
            eip_type = HWCloudEipType.__dict__.get(eip_info['type'], " ")
            temp.append(eip_type[0])
            temp.append(eip_info["bandwidth_name"])
            temp.append(eip_info["bandwidth_id"])
            temp.append(eip_info["bandwidth_size"])
            temp.append(None)
            temp.append(None)
            temp.append(None)
            temp.append(zone_alias)
            temp.append(str(eip_info["create_time"]))
            result_list.append(temp)
        return result_list

    @classmethod
    def parse_ips_v3(cls, eip_list, device_info_dict, zone):
        result_list = list()
        zone_alias = settings.ZONE_ALIAS_DICT.get(zone, zone)
        for eip_info in eip_list:
            temp = list()
            temp.append(eip_info['public_ip_address'])
            temp.append(eip_info['public_ipv6_address'])
            temp.append(eip_info['id'])
            eip_status = HWCloudEipStatus.__dict__.get(eip_info['status'], " ")
            temp.append(eip_status[0])
            eip_type = HWCloudEipType.__dict__.get(eip_info['type'], " ")
            temp.append(eip_type[0])
            temp.append(eip_info['bandwidth']["name"])
            temp.append(eip_info['bandwidth']["id"])
            temp.append(eip_info['bandwidth']["size"])
            # 1.如果ip绑定的是负载均衡,则vnic为空， device_id为associate_instance_id
            # 2.如果ip绑定的是RDS，则device_id为空并且instance_type为RDS， device_id为instance_id
            # 3.如果ip绑定的是PORT, 则很有可能为虚拟ip.
            if not isinstance(eip_info['vnic'], dict):
                device_id = eip_info['associate_instance_id']
                if device_id and device_id in device_info_dict.keys():
                    temp.append(device_info_dict[device_id]["instance_type"])
                    temp.append(device_info_dict[device_id]["name"])
                    temp.append(device_id)
                elif eip_info["status"] != "ACTIVE":
                    temp.append(None)
                    temp.append(None)
                    temp.append(None)
                else:
                    raise Exception("script need to update， reason:1!!!")
            elif not eip_info["vnic"]["device_id"] and eip_info["vnic"]["instance_type"] == "RDS":
                device_id = eip_info["vnic"]["instance_id"]
                if device_id and device_id in device_info_dict.keys():
                    temp.append(device_info_dict[device_id]["instance_type"])
                    temp.append(device_info_dict[device_id]["name"])
                    temp.append(device_id)
                else:
                    raise Exception("script need to update， reason:2!!!")
            elif eip_info["vnic"]["device_id"] and eip_info["vnic"]["device_id"] in device_info_dict.keys():
                temp.append(device_info_dict[eip_info["vnic"]["device_id"]]["instance_type"])
                temp.append(device_info_dict[eip_info["vnic"]["device_id"]]["name"])
                temp.append(eip_info["vnic"]["device_id"])
            elif eip_info["associate_instance_type"] == "PORT":
                temp.append("虚拟IP地址")
                temp.append(eip_info["vnic"]["private_ip_address"])
                temp.append(eip_info["associate_instance_id"])
            else:
                logger.error("eip_info:{}".format(eip_info))
                raise Exception("script need to update， reason:3!!!")
            temp.append(zone_alias)
            temp.append(str(eip_info["created_at"]))
            result_list.append(temp)
        return result_list

    @func_retry()
    def get_data_list(self, project_temp, ak, sk):
        project_id = project_temp["project_id"]
        zone = project_temp["zone"]
        config = self.get_eip_config()
        result_list = list()
        credentials = BasicCredentials(ak, sk, project_id)
        if zone in settings.EIP_V2_ZONE:
            eip_instance = EipInstanceV2(EipClientV2, config, credentials, EndPoint.vpc_endpoint.format(zone))
        else:
            eip_instance = EipInstanceV3(EipClientV3, config, credentials, EndPoint.vpc_endpoint.format(zone))
        nat_instance = NatInstance(NatClient, config, credentials, EndPoint.nat_endpoint.format(zone))
        elb_instance = LoadBalanceInstance(ElbClient, config, credentials, EndPoint.elb_endpoint.format(zone))
        bms_instance = BMSInstance(BmsClient, config, credentials, EndPoint.bms_endpoint.format(zone))
        ecs_instance = EcsInstance(EcsClient, config, credentials, EndPoint.ecs_endpoint.format(zone))
        rds_instance = RdsInstance(RdsClient, config, credentials, EndPoint.rds_endpoint.format(zone))
        query_device_lists = [nat_instance, elb_instance, bms_instance, ecs_instance, rds_instance]
        device_info_dict = self.get_device_info(query_device_lists)
        eip_dict = eip_instance.show_infos()
        if not eip_dict:
            return result_list
        eip_list = eip_instance.parse_response_data(eip_dict)
        if zone in settings.EIP_V2_ZONE:
            result_list = self.parse_ips_v2(eip_list, zone)
        else:
            result_list = self.parse_ips_v3(eip_list, device_info_dict, zone)
        return result_list


def get_eip_info(config_list):
    ret_dict = dict()
    eip_tools = EipTools()
    for config_item in config_list:
        result_list = list()
        username = config_item['account']
        ak = config_item["ak"]
        sk = config_item["sk"]
        project_info = config_item["project_info"]
        logger.info("Collect the username of info:{}".format(username))
        for project_temp in project_info:
            logger.info("Collect the zone of info:{}".format(project_temp["zone"]))
            ret_temp = eip_tools.get_data_list(project_temp, ak, sk)
            result_list.extend(ret_temp or [])
        ret_dict[username] = result_list
    return ret_dict
