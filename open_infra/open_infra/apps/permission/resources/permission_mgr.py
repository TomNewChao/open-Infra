# -*- coding: utf-8 -*-
# @Time    : 2022/10/10 9:30
# @Author  : Tom_zc
# @FileName: permission_mgr.py
# @Software: PyCharm
import traceback
import datetime
import logging
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.db import transaction
from django.db.models import Q
from pytz import timezone as convert_time_zone
from django.conf import settings

from app_resources.models import ServiceInfo
from open_infra.libs.lib_email import EmailBaseLib
from open_infra.utils.utils_git import GitBaseToolsLib, GitBase
from open_infra.utils.utils_kubeconfig import KubeconfigLib
from permission.models import KubeConfigInfo
from open_infra.utils.common import get_suitable_range
from permission.resources.constants import KubeConfigRole
from permission.resources.permission_alarm import KubeconfigAlarm

logger = logging.getLogger("django")


class KubeconfigInteractGitToolsLib(GitBaseToolsLib):

    @classmethod
    def check_params(cls, list_data):
        is_ok, ret_data = True, list()
        for data in list_data:
            if not isinstance(data, dict):
                is_ok = False
                ret_data.append("Parse file fault.")
            if not all([data.get("username"), data.get("role"), data.get("timelimit"), data.get("email"), data.get("cluster"), data.get("namespace")]):
                is_ok = False
                msg = "Whether the input parameters are complete, Please check whether the parameters include " \
                      "UserName, Role, TimeLimit, ServiceName, Email, Cluster, NameSpace."
                ret_data.append(msg)
            if not KubeConfigRole.is_in_kubeconfig_role(data["role"]):
                is_ok = False
                ret_data.append("Role must be in the scope of admin, developer, viewer, Please check Role.")
            if len(data["username"]) > 20 or len(data["username"]) <= 0 or not data["username"].isalnum() or data["username"].lower() != data["username"]:
                is_ok = False
                ret_data.append("Invalid UserName, Please check UserName.")
            if not data["timelimit"].isdigit() or (int(data["timelimit"]) <= 0):
                is_ok = False
                ret_data.append("Invalid TimeLimit, Please check TimeLimit")
            if ServiceInfo.count_namespace(data["namespace"]) == 0:
                is_ok = False
                ret_data.append("The NameSpace is not exist, Please check NameSpace")
            if not KubeconfigLib.is_cluster_exist(data["cluster"]):
                is_ok = False
                ret_data.append("The Cluster is not exist, Please check Cluster")
        if not len(list_data):
            is_ok = False
            ret_data.append("The pr content of parse is empty, Please check the data of submit.")
        if ret_data:
            desc_str = "***{}***".format(",".join(ret_data))
        else:
            desc_str = "***Pending Review by @{}***".format(",@".join(settings.GITHUB_REVIEWER))
        return is_ok, desc_str


class KubeConfigGitBase(GitBase):
    kubeconfig_interact_tools_lib = KubeconfigInteractGitToolsLib

    def parse_create_pr(self):
        if self.pr_dict.get("pull_request"):
            diff_url = self.pr_dict["pull_request"]["diff_url"]
            # patch_url = self.pr_dict["pull_request"]["patch_url"]
        else:
            diff_url = self.pr_dict["issue"]["pull_request"]["diff_url"]
            # patch_url = self.pr_dict["issue"]["pull_request"]["patch_url"]
        content = self.kubeconfig_interact_tools_lib.request_url(diff_url)
        parse_data = self.kubeconfig_interact_tools_lib.parse_diff(content)
        # content = self.kubeconfig_interact_tools_lib.request_url(patch_url)
        # email_str = self.kubeconfig_interact_tools_lib.parse_patch(content)
        is_ok, msg = self.kubeconfig_interact_tools_lib.check_params(parse_data)
        return is_ok, msg, parse_data

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
        url = self.comment_github_url.format(domain, owner, repo, issue_number)
        token = settings.GITHUB_SECRET
        result = self.kubeconfig_interact_tools_lib.request_comment(url, token, comment)
        return result

    def merge_pr(self):
        if self.pr_dict.get("pull_request"):
            list_data = self.pr_dict["pull_request"]["html_url"].split("/")
        else:
            list_data = self.pr_dict["issue"]["pull_request"]["patch_url"].split("/")
        owner = list_data[3]
        repo = list_data[4]
        issue_number = list_data[6]
        domain = settings.GITHUB_DOMAIN
        url = self.merge_github_url.format(domain, owner, repo, issue_number)
        token = settings.GITHUB_SECRET
        result = self.kubeconfig_interact_tools_lib.request_merge(url, token)
        return result


class KubeconfigEmailTool(EmailBaseLib):

    @classmethod
    def get_content(cls, kubeconfig_info):
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
            raise Exception("[KubeconfigEmailTool] ")

    @classmethod
    def _send_email(cls, email_conf):
        """send email"""
        try:
            email_subject = email_conf.get('email_subject')
            email_content = email_conf.get('email_content')
            email_receivers = email_conf.get('email_receivers')
            sender_email = settings.EMAIL_SENDER_EMAIL
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
            cls.send_email(email_receivers, message)
            logger.info("[KubeconfigEmailTool][_send_email] send email success! send data is:{}".format(email_receivers))
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
        kubeconfig_info['email_content'] = cls.get_content(kubeconfig_info)
        return cls._send_email(kubeconfig_info)


# noinspection PyMethodMayBeStatic
class KubeconfigMgr:
    @classmethod
    def create_kubeconfig(cls, kubeconfig_info, dict_data, create_time, merge_at):
        """create new kubeconfig
        @param kubeconfig_info: dict, the parse of dict data
        @param dict_data: dict, the initial of receive params
        @param create_time: create time
        @param merge_at:  merge time
        @return: None or raise Exception()
        """
        need_delete, need_create = dict(), dict()
        username = kubeconfig_info["username"]
        cluster = kubeconfig_info["cluster"]
        namespace = kubeconfig_info["namespace"]
        role = kubeconfig_info["role"]
        timelimit = kubeconfig_info["timelimit"]
        email_str = kubeconfig_info["email"]
        service_name = "{}_{}".format(cluster, namespace)
        kubeconfig_list = KubeConfigInfo.objects.filter(username=username, service_name=service_name)
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
            if len(kubeconfig_list):
                cluster, namespace = kubeconfig_list[0].service_name.split("_")
                dict_data["cluster"] = cluster
                dict_data["namespace"] = namespace
                dict_data["username"] = kubeconfig_list[0].username
                dict_data["role"] = kubeconfig_list[0].role
                KubeconfigLib.delete_kubeconfig(dict_data)
                KubeConfigInfo.objects.filter(username=username, service_name=service_name).delete()
            else:
                logger.info("[create_kubeconfig] There is not exist kubeconfig:{}".format(service_name))
            KubeConfigInfo.objects.create(**create_temp)
        # 2. add generate new kubeconfig, send smail, and modify the status
        with transaction.atomic():
            need_create["username"] = username
            need_create["role"] = role
            need_create["cluster"] = cluster
            need_create["namespace"] = namespace
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
            if not is_send_ok:
                KubeconfigAlarm.active_alarm(username)

    def list(self, kwargs):
        """list kubeconfig info
        @param kwargs: dict, the parse of dict data
        @return: dict
        """
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
