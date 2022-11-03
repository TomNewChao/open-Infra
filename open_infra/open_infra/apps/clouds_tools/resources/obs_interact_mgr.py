# -*- coding: utf-8 -*-
# @Time    : 2022/10/24 20:29
# @Author  : Tom_zc
# @FileName: obs_interact_mgr.py
# @Software: PyCharm
import os
import shutil
import subprocess
import traceback
import threading
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from logging import getLogger
from clouds_tools.models import HWColudObsInteract
from clouds_tools.resources.constants import ObsInteractComment, Community, ScanToolsLock
from open_infra.libs.lib_cloud import HWCloudIAM, HWCloudObs
from open_infra.libs.lib_crypto import AESCrypt
from open_infra.libs.lib_email import EmailBaseLib
from open_infra.tools.scan_obs import ObsTools
from open_infra.utils.common import get_random_password, execute_cmd3_with_tmp, load_yaml
from open_infra.utils.utils_git import GitBaseToolsLib, GitBase, GitHubPrStatus

logger = getLogger("django")


class ObsInteractGitToolsLib(GitBaseToolsLib):
    @classmethod
    def parse_diff(cls, parse_content):
        """Parse the data submitted by git and get it from the pr.diff file"""
        line_list = parse_content.split("\n")
        set_data = set()
        for line in line_list:
            if line.startswith("diff --git"):
                list_content = line.split(r" ")
                path = list_content[-1][1:]
                set_data.add(path)
        list_data = list(set_data)
        logger.info("[parse_diff] parse obs data:{}".format(list_data))
        return list_data

    @classmethod
    def prepare_env(cls, work_dir, git_pr_info, path_list, branch="main", reuse=False):
        """prepare local reposity base and PR branch
        Notice: this will change work directory, action related to obtain path need do before this.
        """
        group = git_pr_info[0]
        repo_name = git_pr_info[1]
        pull_id = git_pr_info[2]
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        repo = group + "/" + repo_name
        git_url = settings.OBS_INTERACT_REPO.format(repo)
        local_path = os.path.join(work_dir, "{}_{}_{}".format(group, repo_name, pull_id))
        try:
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            if os.path.exists(local_path) and not reuse:
                logger.info("WARNING: %s already exist, delete it." % local_path)
                shutil.rmtree(local_path)
            if not os.path.exists(local_path):
                cmd = "cd {} && git clone {} {}".format(work_dir, git_url, local_path)
                if execute_cmd3_with_tmp(cmd)[0] != 0:
                    return False, "Failed to git clone {}".format(git_url), list()
            os.chdir(local_path)
            cmd = "git checkout {}".format(branch)
            if execute_cmd3_with_tmp(cmd)[0] != 0:
                return False, "Failed to checkout {} branch".format(branch), list()
            cmd = "git pull"
            if execute_cmd3_with_tmp(cmd)[0] != 0:
                return False, "Failed to update to latest commit in %s branch".format(branch), list()
            lines = subprocess.getoutput("git branch | grep pr_{n}".format(n=pull_id))
            for br_name in lines.splitlines():
                cmd = "git branch -D {}".format(br_name.strip())
                execute_cmd3_with_tmp(cmd)
            cmd = "git fetch {} pull/{}/head:pr_{}".format(git_url, pull_id, pull_id)
            if execute_cmd3_with_tmp(cmd)[0] != 0:
                return False, "Failed to fetch PR:{n}".format(n=pull_id), list()
            cmd = "git checkout -b working_pr_{}".format(pull_id)
            if execute_cmd3_with_tmp(cmd)[0] != 0:
                return False, "Failed to create working branch working_pr_{n}".format(n=pull_id), list()
            cmd = "git merge --no-edit pr_{}".format(pull_id)
            if execute_cmd3_with_tmp(cmd)[0] != 0:
                return False, "Failed to merge PR:{n} to branch:{base}".format(n=pull_id, base=branch), list()
            list_data = []
            for path in path_list:
                if path.startswith(r"/"):
                    path = path[1:]
                file = os.path.join(local_path, path)
                logger.info("[prepare_env] file path :{}".format(file))
                if os.path.exists(file):
                    data = load_yaml(file)
                    if os.path.basename(path).split(".")[0] == data["username"]:
                        list_data.append(data)
                    else:
                        return False, "The username you entered is inconsistent with the file name", list()
                else:
                    logger.info("[prepare_env] file:{} is not exist".format(file))
            return True, "", list_data
        except Exception as e:
            logger.error("[prepare_env] {}".format(e))
            return False, e, list()
        finally:
            if os.path.exists(local_path):
                os.chdir(work_dir)
                shutil.rmtree(local_path)

    @classmethod
    def parse_data(cls, git_pr_info, path_list):
        """parse data"""
        work_dir = os.path.join(settings.LIB_PATH, "obsconfig")
        return cls.prepare_env(work_dir, git_pr_info, path_list)

    @classmethod
    def check_params(cls, list_data):
        """check params"""
        is_ok, ret_data = True, list()
        for data in list_data:
            if not isinstance(data, dict):
                is_ok = False
                ret_data.append("Parse file fault.")
            if not all([data.get("username"), data.get("community"), data.get("email"), data.get("file_list")]):
                is_ok = False
                msg = "Whether the input parameters are complete, Please check whether the parameters include username, community, email, anonymously_read, file_list"
                ret_data.append(msg)
            elif data.get("anonymously_read") is None:
                is_ok = False
                msg = "Whether the input parameters are complete, Please check whether the parameters include username, community, email, anonymously_read, file_list"
                ret_data.append(msg)
            if not Community.is_in_community(data["community"].lower()):
                is_ok = False
                msg = "Community must be in the scope of Infra, MindSpore, openGauss, openEuler,openLooKeng, Please check Community."
                ret_data.append(msg)
            if len(data["username"]) > 15 or len(data["username"]) <= 0 or not data["username"].isalnum():
                is_ok = False
                ret_data.append("Invalid UserName, Please check UserName.")
            if not isinstance(data["anonymously_read"], bool):
                is_ok = False
                ret_data.append("Invalid anonymously_read, Please check anonymously_read")
            if not isinstance(data["file_list"], list):
                is_ok = False
                ret_data.append("Invalid file_list, File_list must be list")
            for file in data["file_list"]:
                if not isinstance(file, dict):
                    is_ok = False
                    ret_data.append("Invalid file_list, missing file_list keyword")
                if file.get("filename") is None:
                    is_ok = False
                    ret_data.append("Invalid file_list, missing file_list filename")
                if file.get("md5sum") is None:
                    is_ok = False
                    ret_data.append("Invalid file_list, missing file_list md5sum")
        if not len(list_data):
            is_ok = False
            ret_data.append("The pr content of parse is empty, Please check the data of submit.")
        if ret_data:
            desc_str = "***{}***".format(",\n".join(ret_data))
        else:
            desc_str = "***Pending Review by @{}***".format(",@".join(settings.GITHUB_REVIEWER))
        return is_ok, desc_str


class ObsInteractGitBase(GitBase):
    obs_interact_git_tools_lib = ObsInteractGitToolsLib

    # noinspection PyMethodMayBeStatic
    def convert_filed_to_lower(self, parse_data_list):
        """convert filed to lower"""
        ret_list = list()
        for obj_data in parse_data_list:
            dict_temp = dict()
            for key, value in obj_data.items():
                if key.lower().strip() == "community":
                    dict_temp[key.lower()] = value.lower()
                else:
                    dict_temp[key.lower()] = value
            ret_list.append(dict_temp)
        return ret_list

    def parse_create_pr(self):
        """parse pr data"""
        if self.pr_dict.get("pull_request"):
            diff_url = self.pr_dict["pull_request"]["diff_url"]
            list_data = self.pr_dict["pull_request"]["html_url"].split("/")
        else:
            diff_url = self.pr_dict["issue"]["pull_request"]["diff_url"]
            list_data = self.pr_dict["issue"]["pull_request"]["html_url"].split("/")
        owner = list_data[3]
        repo = list_data[4]
        issue_number = list_data[6]
        git_pr_info = (owner, repo, issue_number)
        content = self.obs_interact_git_tools_lib.request_url(diff_url)
        path_list = self.obs_interact_git_tools_lib.parse_diff(content)
        is_ok, msg, parse_data_list = self.obs_interact_git_tools_lib.parse_data(git_pr_info, path_list)
        if not is_ok:
            logger.error("[ObsInteractGitBase] parse create pr:{}, {}, {}".format(is_ok, msg, parse_data_list))
            return is_ok, msg, parse_data_list
        parse_data_list = self.convert_filed_to_lower(parse_data_list)
        logger.info("[ObsInteractGitBase] parse_create_pr:{}".format(list_data))
        is_ok, msg = self.obs_interact_git_tools_lib.check_params(parse_data_list)
        return is_ok, msg, parse_data_list

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
        result = self.obs_interact_git_tools_lib.request_comment(url, token, comment)
        return result

    def merge_pr(self):
        """merge pr"""
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
        result = self.obs_interact_git_tools_lib.request_merge(url, token)
        return result


class ObsInteractEmailTool(EmailBaseLib):

    @classmethod
    def get_content(cls, obs_interact_info):
        """get content
        :param obs_interact_info: include username, password, path
        :return: str or raise e
        """
        try:
            email_content_temp = '''
            尊敬的用户：%s
            您好！
            申请详情信息如下：
            ————————————————————————————————————————————————————————————————————————————
            账户名(云账户)：openeuler
            IAM用户名：%s
            密码：%s
            桶路径：%s
            '''
            realname = obs_interact_info.get("realname")
            username = obs_interact_info.get("username")
            password = obs_interact_info.get("password")
            path = obs_interact_info.get("path")
            email_content = email_content_temp % (realname, username, password, path)
            return email_content
        except Exception as e:
            logger.error('[_get_kubeconfig_email_content] format email content failed,e=%s,t=%s', e.args[0],
                         traceback.format_exc())
            raise Exception("[ObsInteractEmailTool] get email content failed")

    @classmethod
    def _send_email(cls, email_subject, email_content, email_receivers):
        """send email"""
        try:
            sender_email = settings.EMAIL_SENDER_EMAIL
            message = MIMEMultipart()
            message['From'] = Header(sender_email)
            message['To'] = Header(','.join(email_receivers))
            message['Subject'] = Header(email_subject, 'utf-8')
            message.attach(MIMEText(email_content, "plain", "utf-8"))
            cls.send_email(email_receivers, message)
            logger.info("[ObsInteractEmailTool]_send_email send email success! send data is:{}".format(email_receivers))
            return True
        except Exception as e:
            logger.error('[ObsInteractEmailTool]_send_email failed,e=%s,t=%s', e.args[0], traceback.format_exc())
            return False

    @classmethod
    def send_obs_interact_email(cls, obs_interact_info, email_list):
        """send obs_interact email
        @param obs_interact_info: must be dict, include username, password, path
        @param email_list: receive email list
        @return: True or False
        """
        if not isinstance(email_list, list):
            email_list = [email_list]
        if not isinstance(obs_interact_info, dict):
            raise Exception("[send_obs_interact_email] receive param failed:{}".format(obs_interact_info))
        email_subject = settings.OBS_INTERACT_EMAIL_SUBJECT
        email_content = cls.get_content(obs_interact_info)
        return cls._send_email(email_subject, email_content, email_list)


class ObsInteractTools(object):
    @staticmethod
    def get_new_policy(obs_policy_template, default_policy):
        dict_data = dict()
        for policy in obs_policy_template:
            dict_data[policy["Sid"]] = policy
        for policy in default_policy:
            dict_data[policy["Sid"]] = policy
        return list(dict_data.values())


class ObsInteractMgr(object):
    _aes_crypt = AESCrypt()

    @classmethod
    def lgtm_process(cls, obs_interact_git_base, list_data):
        """Handling lgtm processes"""
        with ScanToolsLock.obs_interact_lock:
            for obj_data in list_data:
                try:
                    community = obj_data["community"]
                    real_name = obj_data["username"]
                    is_anonymously_read = obj_data["anonymously_read"]
                    username = "obsi-{}-{}".format(community, real_name)
                    hw_cloud_obs_interact = HWColudObsInteract.objects.filter(username=username,
                                                                              community=community,
                                                                              is_delete=False)
                    # 1.get password and user_id
                    if len(hw_cloud_obs_interact):
                        user_id = hw_cloud_obs_interact[0].user_id
                        encry_password = hw_cloud_obs_interact[0].password
                        password = cls._aes_crypt.decrypt(encry_password)
                    else:
                        # get random password
                        password = get_random_password()
                        encry_password = cls._aes_crypt.encrypt(password)
                        # create user
                        hw_cloud_iam = HWCloudIAM(settings.OBS_AK, settings.OBS_SK, settings.OBS_INTERACT_ZONE)
                        create_user_obj = hw_cloud_iam.create_iam_user(username, password, settings.OBS_DOMAIN_ID)
                        user_id = create_user_obj.user.id
                        # mysql add record
                        HWColudObsInteract.objects.create(
                            username=username,
                            community=community,
                            user_id=user_id,
                            is_delete=False,
                            password=encry_password,
                        )
                    # 2.create dir and set obs_policy
                    with HWCloudObs(settings.OBS_AK, settings.OBS_SK, settings.OBS_BASE_URL) as hw_clouds_obs:
                        path = "{}/{}".format(community, username)
                        dir_path = "{}/".format(path)
                        bucket_name = settings.OBS_INTERACT_BUCEKT_NAME
                        hw_clouds_obs.create_dir(bucket_name, dir_path)
                        old_policy_template = hw_clouds_obs.get_obs_policy(bucket_name)
                        default_policy = hw_clouds_obs.get_obs_default_policy(settings.OBS_DOMAIN_ID, user_id, path, username,
                                                                              is_anonymous_read=is_anonymously_read)
                        new_obs_policy_template = ObsInteractTools.get_new_policy(old_policy_template, default_policy)
                        json_policy = {"Statement": new_obs_policy_template}
                        hw_clouds_obs.set_obs_policy(bucket_name, json_policy)
                    # 3.send email
                    dict_data = {
                        "realname": real_name,
                        "username": username,
                        "password": password,
                        "path": "obs://{}/{}/".format(settings.OBS_INTERACT_BUCEKT_NAME, path)
                    }
                    ObsInteractEmailTool.send_obs_interact_email(dict_data, obj_data["email"])
                    # 4. comment
                    comment = ObsInteractComment.lgtm.format(real_name)
                    obs_interact_git_base.comment_pr(comment)
                except Exception as e:
                    logger.error("[ObsInteractMgr] lgtm_process e:{}, traceback:{}".format(e, traceback.format_exc()))
                    obs_interact_git_base.comment_pr(comment=ObsInteractComment.error)

    @classmethod
    def check_upload_process(cls, obs_interact_git_base, list_data):
        """Handling check_upload processes"""
        with ScanToolsLock.obs_interact_lock:
            list_result = list()
            for obj_data in list_data:
                try:
                    community = obj_data["community"]
                    real_name = obj_data["username"]
                    is_anonymously_read = obj_data["anonymously_read"]
                    username = "obsi-{}-{}".format(community, real_name)
                    obs_prefix = "{}/{}".format(community, username)
                    bucket_name = settings.OBS_INTERACT_BUCEKT_NAME
                    md5sum_dict = {file_obj["filename"]: file_obj["md5sum"] for file_obj in obj_data["file_list"]}
                    with HWCloudObs(settings.OBS_AK, settings.OBS_SK, settings.OBS_BASE_URL) as hw_clouds_obs:
                        md5sum_not_con, sen_file, lack_file, sen_dict = ObsTools.check_bucket_info_and_mdsum(hw_clouds_obs.obs_client,
                                                                                                             md5sum_dict,
                                                                                                             prefix=obs_prefix,
                                                                                                             bucket_name=bucket_name)
                        if len(md5sum_not_con) or len(sen_file) or len(lack_file) or len(sen_dict):
                            sen_data_str = str()
                            for file_name, data in sen_dict.items():
                                sen_data_str += "{}--->{}\n".format(file_name, data)
                            msg = "{}\n{}\n{}\n{}\n{}\n{}".format("md5sum inconsistent files:", ",\n".join(md5sum_not_con),
                                                                  "sensitive files:", ",\n".join(sen_file),
                                                                  "lack files:", ",\n".join(lack_file),
                                                                  "sensitive keywords:", sen_data_str)
                            comment = ObsInteractComment.check_upload_false.format(real_name, msg)
                            obs_interact_git_base.comment_pr(comment)
                            list_result.append(False)
                        else:
                            hw_clouds_obs_interact = HWColudObsInteract.objects.filter(community=community, username=username, is_delete=False)
                            if len(hw_clouds_obs_interact):
                                # modify policy
                                user_id = hw_clouds_obs_interact[0].user_id
                                obs_policy_template = hw_clouds_obs.get_obs_policy(bucket_name)
                                new_obs_policy_template = hw_clouds_obs.get_need_remove_obs_policy(obs_policy_template, username, is_anonymously_read)
                                if len(new_obs_policy_template):
                                    json_policy = {"Statement": new_obs_policy_template}
                                    hw_clouds_obs.set_obs_policy(bucket_name, json_policy)
                                else:
                                    hw_clouds_obs.remove_obs_policy(bucket_name)
                                # remove user
                                hw_cloud_iam = HWCloudIAM(settings.OBS_AK, settings.OBS_SK, settings.OBS_INTERACT_ZONE)
                                hw_cloud_iam.remove_iam_user(user_id)
                                HWColudObsInteract.objects.filter(community=community, username=username).update(is_delete=True)
                            comment = ObsInteractComment.check_upload_ok.format(real_name)
                            obs_interact_git_base.comment_pr(comment)
                            list_result.append(True)
                except Exception as e:
                    logger.error("[ObsInteractMgr] check_upload_process e:{},trace_back:{}".format(e, traceback.format_exc()))
                    obs_interact_git_base.comment_pr(ObsInteractComment.error)
                    list_result.append(False)
            if all(list_result):
                obs_interact_git_base.merge_pr()

    @classmethod
    def merge_process(cls, obs_interact_git_base, list_data):
        """Handling merge processes"""
        with ScanToolsLock.obs_interact_lock:
            for obj_data in list_data:
                try:
                    community = obj_data["community"]
                    real_name = obj_data["username"]
                    is_anonymously_read = obj_data["anonymously_read"]
                    username = "obsi-{}-{}".format(community, real_name)
                    bucket_name = settings.OBS_INTERACT_BUCEKT_NAME
                    with HWCloudObs(settings.OBS_AK, settings.OBS_SK, settings.OBS_BASE_URL) as hw_clouds_obs:
                        comment = ObsInteractComment.check_upload_ok.format(real_name)
                        hw_clouds_obs_interact = HWColudObsInteract.objects.filter(community=community,
                                                                                   username=username,
                                                                                   is_delete=False)
                        if len(hw_clouds_obs_interact):
                            # modify policy
                            user_id = hw_clouds_obs_interact[0].user_id
                            obs_policy_template = hw_clouds_obs.get_obs_policy(bucket_name)
                            new_obs_policy_template = hw_clouds_obs.get_need_remove_obs_policy(obs_policy_template,
                                                                                               username,
                                                                                               is_anonymously_read)
                            if len(new_obs_policy_template):
                                json_policy = {"Statement": new_obs_policy_template}
                                hw_clouds_obs.set_obs_policy(bucket_name, json_policy)
                            else:
                                hw_clouds_obs.remove_obs_policy(bucket_name)
                            # remove user
                            hw_cloud_iam = HWCloudIAM(settings.OBS_AK, settings.OBS_SK, settings.OBS_INTERACT_ZONE)
                            hw_cloud_iam.remove_iam_user(user_id)
                            HWColudObsInteract.objects.filter(community=community, username=username).update(is_delete=True)
                            obs_interact_git_base.comment_pr(comment)
                except Exception as e:
                    logger.error("[ObsInteractMgr] merge_process e:{},trace_back:{}".format(e, traceback.format_exc()))

    @classmethod
    def get_obs_interact(cls, obs_interact_git_base):
        dict_data = obs_interact_git_base.pr_dict
        # logger.error("data is:{}".format(dict_data))
        # new pr
        if GitHubPrStatus.is_in_new_pr_status(dict_data["action"]) and dict_data.get("pull_request") is not None:
            is_ok, msg, list_data = obs_interact_git_base.parse_create_pr()
            if not is_ok:
                logger.error("[get_obs_interact] parse data:{}".format(list_data))
            username = dict_data["pull_request"]["user"]["login"]
            comment = ObsInteractComment.welcome.format(username, is_ok, msg)
            obs_interact_git_base.comment_pr(comment)
        # comment /check
        elif dict_data["action"] == GitHubPrStatus.create and dict_data["comment"].get("body") == "/check":
            is_ok, msg, list_data = obs_interact_git_base.parse_create_pr()
            if not is_ok:
                logger.error("[get_obs_interact] parse data:{}".format(list_data))
            username = dict_data["issue"]["user"]["login"]
            comment = ObsInteractComment.welcome.format(username, is_ok, msg)
            obs_interact_git_base.comment_pr(comment)
        # comment /lgtm
        elif dict_data["action"] == GitHubPrStatus.create and dict_data["comment"].get("body") == "/lgtm":
            username = dict_data["issue"]["user"]["login"]
            comment_username = dict_data["comment"]["user"]["login"]
            if comment_username not in settings.GITHUB_REVIEWER:
                msg = "***@{}***".format(",@".join(settings.GITHUB_REVIEWER))
                comment = ObsInteractComment.valid_lgtm.format(msg)
                obs_interact_git_base.comment_pr(comment)
                return
            is_ok, msg, list_data = obs_interact_git_base.parse_create_pr()
            if not is_ok:
                logger.error("[get_obs_interact] parse data:{}".format(list_data))
                comment = ObsInteractComment.welcome.format(username, is_ok, msg)
                obs_interact_git_base.comment_pr(comment)
                return
            cls.lgtm_process(obs_interact_git_base, list_data)
        # comment /check_upload
        elif dict_data["action"] == GitHubPrStatus.create and dict_data["comment"].get("body") == "/check_upload":
            is_ok, msg, list_data = obs_interact_git_base.parse_create_pr()
            if not is_ok:
                logger.error("[get_obs_interact] parse data:{}".format(list_data))
                return
            t = threading.Thread(target=cls.check_upload_process, args=(obs_interact_git_base, list_data))
            t.start()
        # merge
        elif dict_data["action"] == GitHubPrStatus.closed and dict_data["pull_request"]["merged"]:
            is_ok, msg, list_data = obs_interact_git_base.parse_create_pr()
            if not is_ok:
                logger.error("[get_obs_interact] parse data:{}".format(list_data))
                return
            cls.merge_process(obs_interact_git_base, list_data)

