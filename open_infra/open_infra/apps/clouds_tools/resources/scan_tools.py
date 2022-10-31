# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:34
# @Author  : Tom_zc
# @FileName: scan_tools.py
# @Software: PyCharm
import datetime
import os
import traceback

from django.db import transaction
from django.conf import settings
from threading import Thread, Lock
from logging import getLogger

from clouds_tools.models import HWCloudProjectInfo, HWCloudAccount, HWCloudEipInfo, HWCloudScanEipPortInfo, \
    HWCloudScanEipPortStatus, HWCloudScanObsAnonymousBucket, HWCloudScanObsAnonymousFile, HWCloudScanObsAnonymousStatus, \
    HWCloudHighRiskPort, ServiceInfo
from clouds_tools.resources.constants import NetProtocol, ScanToolsLock, ScanPortStatus, ScanObsStatus, HWCloudEipStatus
from open_infra.libs.lib_cloud import HWCloudObs, HWCloudIAM
from open_infra.utils.common import output_scan_port_excel, output_scan_obs_excel, get_suitable_range, convert_yaml, \
    output_cla_excel, load_yaml
from open_infra.libs.lib_crypto import AESCrypt
from open_infra.utils.default_port_list import HighRiskPort
from open_infra.tools.scan_port import scan_port
from open_infra.tools.scan_obs import ObsTools, scan_obs
from open_infra.tools.scan_sla import scan_cla

logger = getLogger("django")


class ScanOrmTools(object):
    @staticmethod
    def save_scan_eip_port_info_status(tcp_info, udp_info, account_list, creating=True):
        if not isinstance(account_list, list):
            raise Exception("[save_scan_eip_port_info_status] account_list must be list")
        for ip, port_list in tcp_info.items():
            for port_info in port_list:
                dict_data = {
                    "eip": ip,
                    "port": port_info[0],
                    "status": port_info[1],
                    "link_protocol": port_info[2],
                    "transport_protocol": port_info[3],
                    "account": port_info[4],
                    "region": port_info[5],
                    "service_info": port_info[6],
                    "protocol": NetProtocol.TCP
                }
                HWCloudScanEipPortInfo.objects.create(**dict_data)
        for ip, port_list in udp_info.items():
            for port_info in port_list:
                dict_data = {
                    "eip": ip,
                    "port": port_info[0],
                    "status": port_info[1],
                    "link_protocol": port_info[2],
                    "transport_protocol": port_info[3],
                    "account": port_info[4],
                    "region": port_info[5],
                    "service_info": "",
                    "protocol": NetProtocol.UDP
                }
                HWCloudScanEipPortInfo.objects.create(**dict_data)
        logger.error("scan_port save data is:{}".format(str(account_list)))
        if creating:
            status_list = [HWCloudScanEipPortStatus(account=account, status=ScanPortStatus.finish)
                           for account in account_list]
            HWCloudScanEipPortStatus.objects.bulk_create(status_list)
        else:
            HWCloudScanEipPortStatus.objects.filter(account__in=account_list).update(status=ScanPortStatus.finish)

    @staticmethod
    def query_scan_eip_port_status(account):
        try:
            return HWCloudScanEipPortStatus.objects.get(account=account)
        except HWCloudScanEipPortStatus.DoesNotExist:
            logger.error("[query_scan_eip_status] dont find account:{}".format(account))
            return None

    @staticmethod
    def save_scan_eip_port_status(account, status):
        return HWCloudScanEipPortStatus.objects.create(account=account, status=status)

    @staticmethod
    def save_scan_obs_info_status(list_anonymous_bucket, list_anonymous_file, account_list, creating=True):
        for anonymous_data in list_anonymous_bucket:
            dict_data = {
                "account": anonymous_data[0],
                "bucket": anonymous_data[1],
                "url": anonymous_data[2],
            }
            HWCloudScanObsAnonymousBucket.objects.create(**dict_data)
        for anonymous_data in list_anonymous_file:
            dict_data = {
                "account": anonymous_data[0],
                "bucket": anonymous_data[1],
                "url": anonymous_data[2],
                "path": anonymous_data[3],
                "data": anonymous_data[4],
            }
            HWCloudScanObsAnonymousFile.objects.create(**dict_data)
        if creating:
            status_list = [HWCloudScanObsAnonymousStatus(account=account, status=ScanObsStatus.finish)
                           for account in account_list]
            HWCloudScanObsAnonymousStatus.objects.bulk_create(status_list)
        else:
            HWCloudScanObsAnonymousStatus.objects.filter(account__in=account_list).update(
                status=ScanObsStatus.finish)

    @staticmethod
    def query_scan_obs_status(account):
        try:
            return HWCloudScanObsAnonymousStatus.objects.get(account=account)
        except HWCloudScanObsAnonymousStatus.DoesNotExist:
            logger.error("[query_scan_obs_status] dont find account:{}".format(account))
            return None

    @staticmethod
    def save_scan_obs_status(account, status):
        return HWCloudScanObsAnonymousStatus.objects.create(account=account, status=status)

    @staticmethod
    def query_high_risk_port(port):
        try:
            return HWCloudHighRiskPort.objects.get(port=port)
        except HWCloudHighRiskPort.DoesNotExist:
            logger.error("[query_high_risk_port] dont find port:{}".format(port))
            return None


# noinspection PyArgumentList
class ScanBaseTools(object):
    _instance = None
    _aes_crypt = AESCrypt()
    account_info_list = list()
    sla_yaml_list = list()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def get_sla_yaml_config(cls):
        if not cls.sla_yaml_list and not settings.DEBUG:
            ak, sk, url, bucket_name, obs_key = settings.OBS_AK, settings.OBS_SK, settings.OBS_URL, settings.DOWNLOAD_BUCKET_NAME, settings.DOWNLOAD_SLA_KEY_NAME
            content = ObsTools.get_obs_data(ak, sk, url, bucket_name, obs_key)
            cls.sla_yaml_list = convert_yaml(content)
        else:
            cls.sla_yaml_list = load_yaml(os.path.join(settings.BASE_DIR, "config", "sla.yaml"))
        return cls.sla_yaml_list

    @staticmethod
    def get_hw_account_from_obs():
        obs_lib = HWCloudObs(settings.OBS_AK, settings.OBS_SK, settings.OBS_URL)
        content = obs_lib.get_obs_data(settings.DOWNLOAD_BUCKET_NAME, settings.DOWNLOAD_EIP_KEY_NAME)
        return content

    @classmethod
    def get_hw_project_info_from_obs(cls, now_account_info_list):
        if not isinstance(now_account_info_list, list):
            raise Exception("now_account_info_list must be list")
        for account_info in now_account_info_list:
            account_info["project_info"] = HWCloudIAM(account_info["ak"], account_info["sk"]).get_project_zone()

    @classmethod
    def handle_sensitive_data(cls, account_list):
        for account_info in account_list:
            account_info["ak"] = cls._aes_crypt.encrypt(account_info["ak"])
            account_info["sk"] = cls._aes_crypt.encrypt(account_info["sk"])

    @classmethod
    def get_hw_account_project_info_from_obs(cls):
        content = cls.get_hw_account_from_obs()
        cls.get_hw_project_info_from_obs(content)
        cls.handle_sensitive_data(content)
        return content

    @classmethod
    def get_hw_account_project_info_from_database(cls):
        account_list = list()
        account_info_list = HWCloudAccount.objects.all()
        for account_info in account_info_list:
            account_info_dict = account_info.to_dict()
            project_info_list = HWCloudProjectInfo.objects.filter(account__id=account_info_dict["id"])
            account_info_dict["project_info"] = [{"project_id": project_info.id, "zone": project_info.zone} for
                                                 project_info in project_info_list]
            account_list.append(account_info_dict)
        return account_list

    @classmethod
    def handle_encrypt_data(cls, account_list):
        for account_info in account_list:
            account_info["ak"] = cls._aes_crypt.decrypt(account_info["ak"])
            account_info["sk"] = cls._aes_crypt.decrypt(account_info["sk"])

    @classmethod
    def get_decrypt_hw_account_project_info_from_database(cls):
        if not cls.account_info_list:
            account_list = cls.get_hw_account_project_info_from_database()
            cls.handle_encrypt_data(account_list)
            cls.account_info_list = account_list
        return cls.account_info_list

    @staticmethod
    def get_random_cloud_config(ak, sk):
        return HWCloudIAM(ak, sk).get_project_zone()

    @staticmethod
    def get_project_info(ak, sk):
        clouds_config = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        for cloud_info in clouds_config:
            if cloud_info["ak"] == ak and cloud_info["sk"] == sk:
                return cloud_info["project_info"]
        return list()

    @staticmethod
    def parse_scan_eip_query_info(eip_list):
        tcp_list, udp_list = list(), list()
        for eip_info in eip_list:
            if eip_info.protocol == NetProtocol.TCP:
                tcp_list.append(list(eip_info.to_dict().values())[1:-1])
            elif eip_info.protocol == NetProtocol.UDP:
                udp_list.append(list(eip_info.to_dict().values())[1:-1])
        logger.error(tcp_list)
        logger.error(udp_list)
        content = output_scan_port_excel(tcp_list, udp_list)
        return content

    @staticmethod
    def parse_scan_obs_query_info(query_account):
        anonymous_bucket_list, anonymous_file_list, anonymous_data_list = list(), list(), list()
        if isinstance(query_account, list):
            anonymous_bucket_temp = HWCloudScanObsAnonymousBucket.objects.filter(account__in=query_account)
            anonymous_file_temp = HWCloudScanObsAnonymousFile.objects.filter(account__in=query_account)
        else:
            anonymous_bucket_temp = HWCloudScanObsAnonymousBucket.objects.filter(account=query_account)
            anonymous_file_temp = HWCloudScanObsAnonymousFile.objects.filter(account=query_account)
        anonymous_bucket_list.extend([list(data.to_dict().values())[1:] for data in anonymous_bucket_temp])
        anonymous_file_list.extend([list(data.to_dict().values())[1:] for data in anonymous_file_temp])
        return output_scan_obs_excel(anonymous_file_list, anonymous_bucket_list)

    @staticmethod
    def get_account_dict(ak, sk, account):
        account_dict = dict()
        project_info = ScanBaseTools.get_random_cloud_config(ak, sk)
        if not project_info:
            raise Exception("[start_collect_thread] Get empty project info, Failed")
        account_dict["account"] = account
        account_dict["ak"] = ak
        account_dict["sk"] = sk
        account_dict["project_info"] = project_info
        return account_dict


class ScanToolsMgr:
    scan_base_tools = ScanBaseTools()

    @staticmethod
    def get_cloud_account():
        """get all cloud account"""
        account_list = ScanBaseTools.get_decrypt_hw_account_project_info_from_database()
        ret_list = list()
        for account_info in account_list:
            account_temp = dict()
            account_temp["account"] = account_info["account"]
            zone_list = [settings.ZONE_ALIAS_DICT.get(project_temp["zone"], project_temp['zone']) for project_temp in
                         account_info["project_info"]]
            account_temp["zone"] = "，".join(zone_list)
            ret_list.append(account_temp)
        return ret_list


class ScanPortsMgr(ScanToolsMgr):
    def query_data(self, account_list):
        """query progress"""
        config_obj = self.scan_base_tools.get_decrypt_hw_account_project_info_from_database()
        query_account = list()
        for config_info in config_obj:
            if config_info["account"] in account_list:
                query_account.append(config_info["account"])
        eip_list = HWCloudScanEipPortInfo.objects.filter(account__in=query_account)
        return ScanBaseTools.parse_scan_eip_query_info(eip_list)


class SingleScanPortsMgr(ScanToolsMgr):

    @staticmethod
    def collect_thread(account_list):
        """collect data"""
        tcp_info, udp_info, account_name_list = scan_port(account_list)
        with transaction.atomic():
            ScanOrmTools.save_scan_eip_port_info_status(tcp_info, udp_info, account_name_list, creating=False)
        logger.info("[collect_thread] collect high risk port, account:{}".format(account_list[0]["account"]))

    def start_collect_thread(self, ak, sk, account):
        """start a collect thread"""
        try:
            account_dict = ScanBaseTools.get_account_dict(ak, sk, account)
        except Exception as e:
            logger.error("[start_collect_thread] connect:{}, {}".format(e, traceback.format_exc()))
            return 0
        is_blocking = ScanToolsLock.scan_port.acquire(blocking=False)
        if not is_blocking:
            return 1
        try:
            account_status = ScanOrmTools.query_scan_eip_port_status(account)
            if account_status:
                return 2
            ScanOrmTools.save_scan_eip_port_status(account=account, status=ScanPortStatus.handler)
            th = Thread(target=self.collect_thread, args=([account_dict],))
            th.start()
            return 2
        finally:
            ScanToolsLock.scan_port.release()

    # noinspection PyMethodMayBeStatic
    def query_progress(self, account):
        """query progress"""
        content = str()
        account_status = ScanOrmTools.query_scan_eip_port_status(account)
        if not account_status:
            return 0, content
        if account_status.status == ScanPortStatus.handler:
            return 0, content
        eip_list = HWCloudScanEipPortInfo.objects.filter(account=account)
        content = ScanBaseTools.parse_scan_eip_query_info(eip_list)
        return 1, content


class ScanObsMgr(ScanToolsMgr):
    def query_data(self, account_list):
        config_obj = self.scan_base_tools.get_decrypt_hw_account_project_info_from_database()
        query_account = list()
        for config_info in config_obj:
            account = config_info["account"]
            if account in account_list:
                query_account.append(account)
        return ScanBaseTools.parse_scan_obs_query_info(query_account)


class SingleScanObsMgr(ScanToolsMgr):

    @staticmethod
    def collect_thread(account_dict_list):
        """collect data"""
        list_anonymous_bucket, list_sensitive_file, account_list = scan_obs(account_dict_list)
        with transaction.atomic():
            ScanOrmTools.save_scan_obs_info_status(list_anonymous_bucket, list_sensitive_file, account_list,
                                                   creating=False)

    def start_collect_thread(self, ak, sk, account):
        """start a collect thread"""
        try:
            eip_tools = ObsTools()
            eip_tools.get_all_bucket(ak, sk, settings.OBS_BASE_URL, inhibition_fault=False)
            account_dict = ScanBaseTools.get_account_dict(ak, sk, account)
        except Exception as e:
            logger.error("[SingleScanObs] start_collect_thread connect:{}, {}".format(e, traceback.format_exc()))
            return 0
        is_blocking = ScanToolsLock.scan_obs.acquire(blocking=False)
        if not is_blocking:
            return 1
        try:
            account_status = ScanOrmTools.query_scan_obs_status(account)
            if account_status:
                return 2
            ScanOrmTools.save_scan_obs_status(account, ScanObsStatus.handler)
            th = Thread(target=self.collect_thread, args=([account_dict],))
            th.start()
            return 2
        finally:
            ScanToolsLock.scan_obs.release()

    # noinspection PyMethodMayBeStatic
    def query_progress(self, account):
        """query progress"""
        content = str()
        account_status = ScanOrmTools.query_scan_obs_status(account)
        if not account_status:
            return 0, content
        if account_status.status == ScanObsStatus.handler:
            return 0, content
        content = ScanBaseTools.parse_scan_obs_query_info(account)
        return 1, content


# noinspection PyMethodMayBeStatic
class HighRiskPortMgr(ScanToolsMgr):
    _create_lock = Lock()

    def list(self, kwargs):
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        if filter_name and filter_name == "port":
            eip_list = HWCloudHighRiskPort.objects.filter(port__contains=filter_value)
        else:
            eip_list = HWCloudHighRiskPort.objects.all()
        total = len(eip_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "create_time"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        eip_list = eip_list.order_by(order_by)
        task_list = [task.to_dict() for task in eip_list[slice_obj]]
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": task_list
        }
        return res

    def create(self, port, desc):
        with HighRiskPortMgr._create_lock:
            if ScanOrmTools.query_high_risk_port(port):
                return 1
            HWCloudHighRiskPort.objects.create(port=port, desc=desc)
            HighRiskPort.cur_port_dict.update({port: desc})
            return 0

    def delete(self, port_list):
        HWCloudHighRiskPort.objects.filter(port__in=port_list).delete()
        for port in port_list:
            if port in HighRiskPort.cur_port_dict.keys():
                del HighRiskPort.cur_port_dict[port]
        return True


# noinspection PyMethodMayBeStatic
class EipMgr(ScanToolsMgr):

    def list_eip(self, kwargs):
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        if filter_name and filter_name == "eip":
            eip_list = HWCloudEipInfo.objects.filter(eip__contains=filter_value)
        elif filter_name and filter_name == "example_id":
            eip_list = HWCloudEipInfo.objects.filter(example_id__contains=filter_value)
        elif filter_name and filter_name == "example_name":
            eip_list = HWCloudEipInfo.objects.filter(example_name__contains=filter_value)
        elif filter_name and filter_name == "account":
            eip_list = HWCloudEipInfo.objects.filter(account__contains=filter_value)
        elif filter_name and filter_name == "eip_type":
            filter_value = HWCloudEipStatus.get_comment_status().get(filter_value, -1)
            eip_list = HWCloudEipInfo.objects.filter(eip_status__contains=filter_value)
        elif filter_name and filter_name == "eip_zone":
            eip_list = HWCloudEipInfo.objects.filter(eip_zone__contains=filter_value)
        else:
            eip_list = HWCloudEipInfo.objects.all()
        total = len(eip_list)
        page, slice_obj = get_suitable_range(total, page, size)
        # 排序, 0-升序
        order_by = order_by if order_by else "create_time"
        order_type = order_type if order_type else 0

        if order_type != 0:
            order_by = "-" + order_by

        eip_list = eip_list.order_by(order_by)

        task_list = [task.to_dict() for task in eip_list[slice_obj]]

        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": task_list
        }
        return res


# noinspection PyMethodMayBeStatic
class SlaMgr:
    _ignore_service_name_alias = ["Ascend-repo", "openEuler Jenkins ISO", "Ptadapter Jenkins"]

    def query_all_sla_info(self):
        """query all sla info from uptime-robot"""
        cur_date = datetime.datetime.now()
        logger.info("[SlaMgr] query_all_sla_info query year:{} month:{} day:{}".format(cur_date.year, cur_date.month, cur_date.day))
        sla_detail_list = scan_cla(year=int(cur_date.year), month=int(cur_date.month), day=int(cur_date.day))
        sla_info_list = ScanBaseTools.get_sla_yaml_config()
        sla_info_dict = {sla_info["name-alias"]: {"introduce": sla_info["introduce"], "name": sla_info.get("name", "")} for sla_info in sla_info_list}
        ret_list = list()
        for sla_temp in sla_detail_list:
            ret_dict = dict()
            del sla_temp[0]
            if sla_temp[0] in self._ignore_service_name_alias:
                continue
            sla_data = sla_info_dict.get(sla_temp[0], dict())
            ret_dict["name-alias"] = sla_temp[0]
            ret_dict["name"] = sla_data.get("name")
            ret_dict["introduce"] = sla_data.get("introduce")
            ret_dict["sla_url"] = sla_temp[-1]
            ret_dict["sla_zone"] = settings.CLA_EXPLAIN.get(sla_temp[3].lower())
            ret_dict["month_exp_min"] = sla_temp[4]
            ret_dict["year_exp_min"] = sla_temp[5]
            ret_dict["month_sla"] = sla_temp[6].replace("%", "")
            ret_dict["year_sla"] = sla_temp[7].replace("%", "")
            ret_dict["sla_year_remain"] = round(sla_temp[8], 4)
            ret_list.append(ret_dict)
        return ret_list

    def list(self, kwargs):
        """The list of service"""
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        if filter_name and filter_name == "service_name":
            service_info_list = ServiceInfo.objects.filter(service_name__contains=filter_value)
        elif filter_name and filter_name == "namespace":
            service_info_list = ServiceInfo.objects.filter(namespace__contains=filter_value)
        elif filter_name and filter_name == "cluster":
            service_info_list = ServiceInfo.objects.filter(cluster__contains=filter_value)
        elif filter_name and filter_name == "url":
            service_info_list = ServiceInfo.objects.filter(url__contains=filter_value)
        else:
            service_info_list = ServiceInfo.objects.all()
        total = len(service_info_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "create_time"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        service_result_list = service_info_list.order_by(order_by).values(
            "service_name", "service_alias", "namespace", "cluster",
            "service_introduce", "url_alias", "community", "month_abnormal_time",
            "year_abnormal_time", "month_sla", "year_sla", "remain_time")
        ret_list = list()
        for task in service_result_list[slice_obj]:
            if task["month_sla"]:
                task["month_sla"] = "{}%".format(task["month_sla"])
            if task["year_sla"]:
                task["year_sla"] = "{}%".format(task["year_sla"])
            ret_list.append(task)
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": ret_list
        }
        return res

    def export(self):
        service_info_list = ServiceInfo.objects.filter().exclude(service_alias=None).order_by("remain_time").values(
            "service_alias", "service_introduce", "url_alias",
            "community", "month_abnormal_time", "year_abnormal_time",
            "month_sla", "year_sla", "remain_time")
        return output_cla_excel(service_info_list)
