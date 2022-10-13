# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 9:30
# @Author  : Tom_zc
# @FileName: permission_mgr.py
# @Software: PyCharm
import abc
import re
import smtplib
import traceback
import datetime
import requests
import logging
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.db import transaction
from django.db.models import Q
from pytz import timezone as convert_time_zone
from django.conf import settings
from open_infra.utils.kubeconfig_lib import KubeconfigLib
from permission.models import KubeConfigInfo, ServiceInfo
from open_infra.utils.common import get_suitable_range
from permission.resources.constants import PermissionGlobalConfig, KubeConfigRole

logger = logging.getLogger("django")


class PrBase(metaclass=abc.ABCMeta):
    Pr_Base_lib = None

    def __init__(self, pr_dict):
        self.pr_dict = pr_dict

    def create_pr(self):
        raise NotImplemented

    def comment_pr(self, comment):
        raise NotImplemented

    def merge_pr(self):
        raise NotImplemented


class PrBaseLib(object):
    @classmethod
    def request_comment(cls, url, token, body_data, timeout=60):
        raise NotImplemented

    @classmethod
    def request_diff(cls, url, timeout=60):
        raise NotImplemented

    @classmethod
    def request_merge(cls, url, token, timeout=60):
        raise NotImplemented

    @classmethod
    def parse_diff(cls, parse_content):
        raise NotImplemented

    @classmethod
    def check_params(cls, list_data):
        raise NotImplemented


class GitHubPrLib(PrBaseLib):
    @classmethod
    def request_comment(cls, url, token, body_data, timeout=60):
        header = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer {}".format(token)
        }
        result = requests.post(url, headers=header, json={"body": body_data}, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception(
                "[request_comment] request url:{} failed,code:{}, content:{}".format(url, result.content,
                                                                                     result.content))
        return result

    @classmethod
    def request_url(cls, url, timeout=60):
        result = requests.get(url, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception(
                "[request_diff] request url:{} failed,code:{}, content:{}".format(url, result.content, result.content))
        return result.content.decode("utf-8")

    @classmethod
    def request_merge(cls, url, token, timeout=60):
        header = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer {}".format(token)
        }
        result = requests.put(url, headers=header, timeout=(timeout, timeout))
        if not str(result.status_code).startswith("2"):
            raise Exception(
                "[request_merge] request url:{} failed,code:{}, content:{}".format(url, result.content, result.content))
        return result

    @classmethod
    def parse_diff(cls, parse_content):
        result_list = parse_content.split("+++ ")
        list_data = list()
        for result in result_list:
            dict_data = dict()
            for line in result.split("\n"):
                if line.startswith("+") and not line.startswith("++"):
                    list_line = line[1:].split(":")
                    if len(list_line) != 2:
                        continue
                    dict_data[list_line[0].strip().lower()] = list_line[1].strip()
            if len(dict_data):
                list_data.append(dict_data)
        logger.info("[parse_diff] parse data:{}".format(list_data))
        return list_data

    @classmethod
    def parse_patch(cls, parse_content):
        result_list = parse_content.split("+++ ")
        email_str = str()
        for result in result_list:
            for line in result.split("\n"):
                if line.startswith("From:"):
                    email_temp = re.findall(r"<.*?>", line)
                    if len(email_temp):
                        email_str = email_temp[0][1:-1]
                        break
        logger.info("[parse_patch] parse email:{}".format(email_str))
        return email_str

    @classmethod
    def check_params(cls, list_data):
        is_ok, ret_data = True, list()
        for data in list_data:
            if not isinstance(data, dict):
                is_ok = False
                ret_data.append("Parse file fault.")
            elif not data.get("username") or not data.get("role") or not data.get("timelimit") or not data.get("servicename"):
                is_ok = False
                ret_data.append(
                    "Whether the input parameters are complete, Please check whether the parameters include UserName, Role, TimeLimit, ServiceName.")
            elif not KubeConfigRole.is_in_kubeconfig_role(data["role"]):
                is_ok = False
                ret_data.append("Role must be in the scope of admin, developer, viewer, Please check Role.")
            elif len(data["username"]) > 20 or len(data["username"]) <= 0 or not data["username"].isalnum() or data["username"].lower() != data["username"]:
                is_ok = False
                ret_data.append("Invalid UserName, Please check UserName.")
            elif not data["timelimit"].isdigit() or (int(data["timelimit"]) <= 0):
                is_ok = False
                ret_data.append("Invalid TimeLimit, Please check TimeLimit")
            elif len(ServiceInfo.objects.filter(service_name=data["servicename"])) == 0:
                is_ok = False
                ret_data.append("Invalid ServiceName, Please check ServiceName.")
        if ret_data:
            desc_str = "***{}***".format(",".join(ret_data))
        else:
            desc_str = "***Pending Review by @{}***".format(",".join(settings.GITHUB_REVIEWER))
        return is_ok, desc_str


class GitHubPr(PrBase):
    Pr_Base_lib = GitHubPrLib

    def parse_create_pr(self):
        if self.pr_dict.get("pull_request"):
            diff_url = self.pr_dict["pull_request"]["diff_url"]
            patch_url = self.pr_dict["pull_request"]["patch_url"]
        else:
            diff_url = self.pr_dict["issue"]["pull_request"]["diff_url"]
            patch_url = self.pr_dict["issue"]["pull_request"]["patch_url"]
        content = self.Pr_Base_lib.request_url(diff_url)
        parse_data = self.Pr_Base_lib.parse_diff(content)
        content = self.Pr_Base_lib.request_url(patch_url)
        email_str = self.Pr_Base_lib.parse_patch(content)
        is_ok, msg = self.Pr_Base_lib.check_params(parse_data)
        return is_ok, msg, parse_data, email_str

    def comment_pr(self, comment):
        """comment pr"""
        if self.pr_dict.get("pull_request"):
            list_data = self.pr_dict["pull_request"]["html_url"].split("/")
        else:
            list_data = self.pr_dict["issue"]["pull_request"]["patch_url"].split("/")
        owner = list_data[3]
        repo = list_data[4]
        issue_number = list_data[6]
        domain = settings.GITHUB_DOMAIN
        url = PermissionGlobalConfig.comment_github_url.format(domain, owner, repo, issue_number)
        token = settings.GITHUB_SECRET
        result = self.Pr_Base_lib.request_comment(url, token, comment)
        return result

    def merge_pr(self):
        list_data = self.pr_dict["pull_request"]["html_url"].split("/")
        owner = list_data[3]
        repo = list_data[4]
        issue_number = list_data[6]
        domain = settings.GITHUB_DOMAIN
        url = PermissionGlobalConfig.merge_github_url.format(domain, owner, repo, issue_number)
        token = settings.GITHUB_SECRET
        result = self.Pr_Base_lib.request_merge(url, token)
        return result


class KubeconfigEmailTool(object):

    @classmethod
    def _get_kubeconfig_email_content(cls, kubeconfig_info):
        """根据类型返回对应模板
        :param kubeconfig_info:
        :return:
        """
        try:
            email_content_temp = '''
            尊敬的用户：%s
            您好！
            请查收申请的kubeconfig文件，详见附件文件。
            申请详情信息如下：
            ————————————————————————————————————————————————————————————————————————————
            创建角色：%s
            命名空间：%s
            创建时间：%s
            审核时间：%s
            过期天数：%s天
            过期截止时间：%s
            '''
            create_time = kubeconfig_info.get("create_time")
            expired_time = int(kubeconfig_info.get("expired_time"))
            review_time = kubeconfig_info.get('review_time')
            if isinstance(create_time, datetime.datetime):
                str_deadline_time = review_time + datetime.timedelta(days=int(expired_time))
                str_deadline_time = str_deadline_time.astimezone(convert_time_zone('Asia/Shanghai')).strftime(
                    '%Y-%m-%d %H:%M:%S')
                create_time = create_time.astimezone(convert_time_zone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                review_time = review_time.astimezone(convert_time_zone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            else:
                create_time = datetime.datetime.strptime(create_time, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(
                    hours=8)
                review_time = datetime.datetime.strptime(review_time, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(
                    hours=8)
                str_deadline_time = review_time + datetime.timedelta(days=int(expired_time))
            email_content = email_content_temp % (kubeconfig_info.get('username'),
                                                  kubeconfig_info.get('role'),
                                                  kubeconfig_info.get('namespace'),
                                                  str(create_time),
                                                  str(review_time),
                                                  str(expired_time),
                                                  str_deadline_time)
            return email_content
        except Exception as e:
            logger.error('[_get_kubeconfig_email_content] format email content failed,e=%s,t=%s', e.args[0],
                         traceback.format_exc())

    @classmethod
    def _send_email(cls, email_conf):
        """send email"""
        try:
            email_subject = email_conf.get('email_subject')
            email_content = email_conf.get('email_content')
            email_receivers = email_conf.get('email_receivers')
            sender_email = settings.ALARM_EMAIL_SENDER_EMAIL
            server_address = settings.ALARM_EMAIL_SENDER_SERVER
            server_port = int(settings.ALARM_EMAIL_SENDER_PORT)
            # text
            message = MIMEMultipart()
            message['From'] = Header(sender_email)
            message['To'] = Header(','.join(email_receivers))
            message['Subject'] = Header(email_subject, 'utf-8')
            # content
            message.attach(MIMEText(email_content, "plain", "utf-8"))
            # attachment
            file_name = "{}-{}".format(email_conf["cluster"], email_conf["namespace"])
            attachment = MIMEText(email_conf["attachment_content"], 'base64', 'utf-8')
            attachment["Content-Type"] = 'application/octet-stream'
            attachment["Content-Disposition"] = 'attachment;filename="{}"'.format(file_name)
            message.attach(attachment)

            if not settings.IS_SSL:
                smt_obj = smtplib.SMTP(server_address, port=int(server_port))
                smt_obj.login(settings.ALARM_EMAIL_USERNAME, settings.ALARM_EMAIL_PWD)
                smt_obj.starttls()
                smt_obj.sendmail(sender_email, email_receivers, message.as_string())
            else:
                smt_obj = smtplib.SMTP_SSL(server_address, port=int(server_port))
                smt_obj.login(settings.ALARM_EMAIL_USERNAME, settings.ALARM_EMAIL_PWD)
                smt_obj.sendmail(sender_email, email_receivers, message.as_string())
            logger.info(
                "[KubeconfigEmailTool][_send_email] send email success! send data is:{}".format(email_receivers))
            return True
        except Exception as e:
            logger.error('[KubeconfigEmailTool] send email failed,e=%s,t=%s', e.args[0], traceback.format_exc())
            return False

    @classmethod
    def send_kubeconfig_email(cls, kubeconfig_info, email_list):
        """send kubeconfig email
        @param kubeconfig_info: must be dict
        @param email_list: receive email list
        @return: True or False
        """
        if not isinstance(kubeconfig_info, dict):
            raise Exception("[send_kubeconfig_email] receive param failed")
        kubeconfig_info['email_receivers'] = email_list
        kubeconfig_info['email_subject'] = settings.KUBECONFIG_EMAIL_SUBJECT
        kubeconfig_info['email_content'] = cls._get_kubeconfig_email_content(kubeconfig_info)
        return cls._send_email(kubeconfig_info)


# noinspection PyMethodMayBeStatic
class KubeconfigMgr:
    @classmethod
    def create_kubeconfig(cls, kubeconfig_info, dict_data, email_str, create_time, merge_at):
        """create new kubeconfig
        @param kubeconfig_info: dict, the parse of dict data
        @param dict_data: dict, the initial of receive params
        @param email_str:  email
        @param create_time: create time
        @param merge_at:  merge time
        @return: None or raise Exception()
        """
        need_delete, need_create = dict(), dict()
        username = kubeconfig_info["username"]
        service_name = kubeconfig_info["servicename"]
        role = kubeconfig_info["role"]
        timelimit = kubeconfig_info["timelimit"]
        kubeconfig_list = KubeConfigInfo.objects.filter(username=username).filter(service_name=service_name)
        service_info_list = ServiceInfo.objects.filter(service_name=service_name)
        # 1.add new record, if exist before, and delete record and kubeconfig
        with transaction.atomic():
            create_temp = {
                "username": username,
                "email": email_str,
                "role": role,
                "service_name": service_name,
                "create_time": create_time,
                "review_time": merge_at,
                "expired_time": timelimit,
                "send_ok": False
            }
            if len(kubeconfig_list) and len(service_info_list):
                dict_data["username"] = kubeconfig_list[0].username
                dict_data["role"] = kubeconfig_list[0].role
                dict_data["namespace"] = service_info_list[0].namespace
                dict_data["cluster"] = service_info_list[0].cluster
                KubeconfigLib.delete_kubeconfig(dict_data)
                KubeConfigInfo.objects.filter(username=username).filter(service_name=service_name).delete()
                KubeConfigInfo.objects.create(**create_temp)
            elif len(service_info_list):
                KubeConfigInfo.objects.create(**create_temp)
            else:
                raise Exception("service name:{} not exist...".format(service_name))
        # 2. add generate new kubeconfig, send smail, and modify the status
        with transaction.atomic():
            need_create["username"] = username
            need_create["role"] = role
            need_create["namespace"] = service_info_list[0].namespace
            need_create["cluster"] = service_info_list[0].cluster
            need_create["url"] = service_info_list[0].url
            is_ok, content = KubeconfigLib.create_kubeconfig(need_create)
            if not is_ok:
                raise Exception("[KubeConfigView] create kubeconfig:{}".format(content))
            email_list = [email_str, ]
            need_create["create_time"] = create_time
            need_create["review_time"] = merge_at
            need_create["expired_time"] = timelimit
            need_create["attachment_content"] = content
            is_send_ok = KubeconfigEmailTool.send_kubeconfig_email(need_create, email_list)
            KubeConfigInfo.objects.filter(username=username).filter(service_name=service_name).update(
                send_ok=is_send_ok)

    def list(self, kwargs):
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        if filter_name and filter_name == "username":
            kubeconfig_info_list = KubeConfigInfo.objects.filter(username__contains=filter_value)
        elif filter_name and filter_name == "email":
            kubeconfig_info_list = KubeConfigInfo.objects.filter(email__contains=filter_value)
        elif filter_name and filter_name == "role":
            kubeconfig_info_list = KubeConfigInfo.objects.filter(role__contains=filter_value)
        elif filter_name and filter_name == "service_name":
            kubeconfig_info_list = KubeConfigInfo.objects.filter(service_name__contains=filter_value)
        elif filter_name and filter_name == "send_ok":
            if filter_value == "是":
                kubeconfig_info_list = KubeConfigInfo.objects.filter(send_ok=True)
            elif filter_value == "否":
                kubeconfig_info_list = KubeConfigInfo.objects.filter(send_ok=True)
            else:
                kubeconfig_info_list = KubeConfigInfo.objects.filter(~Q(send_ok__in=[True, False]))
        else:
            kubeconfig_info_list = KubeConfigInfo.objects.all()
        total = len(kubeconfig_info_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "create_time"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        eip_list = kubeconfig_info_list.order_by(order_by)
        task_list = [task.to_dict() for task in eip_list[slice_obj]]
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": task_list
        }
        return res


# noinspection PyMethodMayBeStatic
class ServiceInfoMgr:

    def list(self, kwargs):
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
        eip_list = service_info_list.order_by(order_by)
        task_list = [task.to_dict() for task in eip_list[slice_obj]]
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": task_list
        }
        return res
