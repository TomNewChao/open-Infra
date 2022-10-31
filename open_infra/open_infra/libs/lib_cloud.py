# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:21
# @Author  : Tom_zc
# @FileName: lib_cloud.py
# @Software: PyCharm

import json
import traceback
from obs import ObsClient
from logging import getLogger
from django.conf import settings
from collections import defaultdict
from open_infra.utils.common import convert_yaml
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkcore.exceptions.exceptions import ClientRequestException
from huaweicloudsdkcore.http.http_config import HttpConfig
from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkiam.v3.region.iam_region import IamRegion
from huaweicloudsdkiam.v3 import *

logger = getLogger("django")


class HWCloudObs(object):
    def __init__(self, ak=None, sk=None, url=None, obs_client=None):
        if obs_client is None:
            self.obs_client = ObsClient(access_key_id=ak,
                                        secret_access_key=sk,
                                        server=url)
        else:
            self.obs_client = obs_client

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.obs_client:
            self.obs_client.close()

    def upload_obs_data(self, upload_bucket, upload_key, upload_data):
        """Upload obs data"""
        if not isinstance(upload_data, dict):
            raise Exception("upload_data must be dict")
        content = str()
        resp = self.obs_client.getObject(upload_bucket, upload_key, loadStreamInMemory=False)
        if resp.status < 300:
            while True:
                chunk = resp.body.response.read(65536)
                if not chunk:
                    break
                content = "{}{}".format(content, chunk.decode("utf-8"))
            resp.body.response.close()
        elif resp.errorCode == "NoSuchKey":
            logger.info("Key:{} is not exist, need to create".format(upload_key))
        else:
            logger.error('errorCode:', resp.errorCode)
            logger.error('errorMessage:', resp.errorMessage)
            raise Exception("get object failed：{}....".format(upload_key))
        if content:
            read_dict_data = json.loads(content)
        else:
            read_dict_data = dict()
        for domain, domain_info in upload_data.items():
            read_dict_data[domain] = domain_info
        new_content = json.dumps(read_dict_data)
        response = self.obs_client.putContent(upload_bucket, upload_key, new_content)
        if response.status != 200:
            raise Exception("upload credentials failed!")

    def get_obs_data(self, download_bucket, download_key):
        """down obs data"""
        content = str()
        resp = self.obs_client.getObject(download_bucket, download_key, loadStreamInMemory=False)
        if resp.status < 300:
            while True:
                chunk = resp.body.response.read(65536)
                if not chunk:
                    break
                content = "{}{}".format(content, chunk.decode("utf-8"))
            resp.body.response.close()
        elif resp.errorCode == "NoSuchKey":
            logger.info("Key:{} is not exist, need to create".format(download_key))
            raise Exception("get object failed(no such key):{}...".format(download_key))
        else:
            logger.error('errorCode:{}'.format(resp.errorCode))
            logger.error('errorMessage:{}'.format(resp.errorMessage))
            raise Exception("get object failed：{}....".format(download_key))
        now_account_info_list = convert_yaml(content)
        return now_account_info_list

    def create_dir(self, bucket_name, path):
        """创建文件夹, 可建立多层级
        :param path: 以/结尾， eg: openeuler/zhuchao/1362256633/
        :param bucket_name: 桶名
        :return:
        """
        try:
            resp = self.obs_client.putContent(bucket_name, path, content=None)
            if resp.status < 300:
                return True
            else:
                raise Exception('errorCode:{}, errorMessage:{}'.format(resp.errorCode, resp.errorMessage))
        except Exception as e:
            logger.error("e:{}, traceback:{}".format(e, traceback.format_exc()))
            return False

    @staticmethod
    def get_obs_default_policy(domain_id, user_id, path, username, is_anonymous_read=False):
        json_policy = {
            "Statement": [
                {
                    "Sid": "user-{}".format(username),
                    "Effect": "Allow",
                    "Principal": {
                        "ID": [
                            "domain/{}:user/{}".format(domain_id, user_id),
                        ]
                    },
                    "Action": [
                        "ListBucket",
                        "HeadBucket",
                        "GetBucketLocation",
                        "GetBucketStorage",
                        "GetObject",
                        "PutObject",
                        "RestoreObject",
                        "DeleteObject",
                        "GetObjectAcl",
                        "PutObjectAcl",
                        "GetObjectVersion",
                        "DeleteObjectVersion",
                        "GetObjectVersionAcl",
                        "PutObjectVersionAcl",
                        "AbortMultipartUpload",
                        "ListMultipartUploadParts",
                        "ModifyObjectMetaData"
                    ],
                    "Resource": [
                        "obs-transfer",
                        "obs-transfer/{}/".format(path),
                        "obs-transfer/{}/*".format(path)
                    ]
                }
            ]
        }
        if is_anonymous_read:
            anonymous_dict = {
                "Sid": "anonymous-{}".format(username),
                "Effect": "Allow",
                "Principal": {
                    "ID": ["*"]
                },
                "Action": ["ListBucket", "HeadBucket", "GetBucketLocation",
                           "ListBucketVersions", "GetObject", "RestoreObject",
                           "GetObjectAcl", "GetObjectVersion", "GetObjectVersionAcl"],
                "Resource": [
                    "obs-transfer",
                    "obs-transfer/{}/*".format(path)
                ]
            }
            json_policy["Statement"].append(anonymous_dict)
        return json_policy["Statement"]

    @staticmethod
    def get_need_remove_obs_policy(obs_policy_template, username, is_anonymously_read):
        new_obs_policy_template = defaultdict(list)
        for policy in obs_policy_template:
            if policy.Sid == "user-{}".format(username):
                logger.info("[HWCloudObs] get_need_remove_obs_policy delete policy sid:{}".format(policy.Sid))
            elif policy.Sid == "anonymous-{}".format(username) and not is_anonymously_read:
                logger.info("[HWCloudObs] get_need_remove_obs_policy delete policy sid:{}".format(policy.Sid))
            else:
                new_obs_policy_template["Statement"].append(policy)
        return new_obs_policy_template

    def get_obs_policy(self, bucket_name):
        resp = self.obs_client.getBucketPolicy(bucket_name)
        if resp.status < 300:
            policy_json = json.loads(resp.body.policyJSON)
            return policy_json["Statement"]
        elif resp.errorCode == "NoSuchBucketPolicy":
            return list()
        else:
            raise Exception('errorCode:{}, errorMessage:{}'.format(resp.errorCode, resp.errorMessage))

    def set_obs_policy(self, bucket_name, json_policy):
        try:
            resp = self.obs_client.setBucketPolicy(bucket_name, json_policy)
            if resp.status < 300:
                return True
            else:
                raise Exception('errorCode:{}, errorMessage:{}'.format(resp.errorCode, resp.errorMessage))
        except Exception as e:
            print("e:{}, traceback:{}".format(e, traceback.format_exc()))
            return False

    def remove_obs_policy(self, bucket_name):
        try:
            resp = self.obs_client.deleteBucketPolicy(bucket_name)
            if resp.status < 300:
                print('requestId:', resp.requestId)
                return True
            else:
                raise Exception('errorCode:{}, errorMessage:{}'.format(resp.errorCode, resp.errorMessage))
        except Exception as e:
            print("e:{}, traceback:{}".format(e, traceback.format_exc()))
            return False


class HWCloudIAM(object):
    def __init__(self, ak, sk, zone="ap-southeast-1"):
        self.ak = ak
        self.sk = sk
        config = self.get_iam_config()
        credentials = GlobalCredentials(self.ak, self.sk)
        self.client = IamClient.new_builder().with_http_config(config) \
            .with_credentials(credentials) \
            .with_region(IamRegion.value_of(zone)) \
            .build()

    @classmethod
    def get_iam_config(cls):
        config = HttpConfig.get_default_config()
        config.ignore_ssl_verification = True
        config.retry_times = 1
        config.timeout = (180, 180)
        return config

    def get_project_zone(self):
        list_data = list()
        try:
            request = KeystoneListProjectsRequest()
            response = self.client.keystone_list_projects(request)
            for info in response.projects:
                if info.name in settings.IGNORE_ZONE:
                    continue
                list_data.append({"zone": info.name, "project_id": info.id})
            logger.info("[get_project_zone] collect project total:{}".format(len(list_data)))
            return list_data
        except exceptions.ClientRequestException as e:
            msg = "[HWCloudIAM] ak:{}, sk:{} get project zone failed:{},{},{},{}".format(self.ak[:5], self.sk[:5],
                                                                                         e.status_code, e.request_id,
                                                                                         e.error_code, e.error_msg)
            logger.error(msg)
            return list_data

    # noinspection PyTypeChecker
    def create_iam_user(self, username, password, domain_id):
        ret = None
        try:
            data = {
                "user": {
                    "name": username,
                    "domain_id": domain_id,
                    "password": password
                }
            }
            req = CreateUserRequest(body=data)
            ret = self.client.create_user(req)
        except ClientRequestException as e:
            msg = json.loads(e.error_msg)
            if str(msg["errorcode"][0]) == "1109":
                logger.error("[HWCloudIAM] create iam user: user is exist:{}".format(e))
            else:
                raise e
        return ret

    def remove_iam_user(self, user_id):
        req = KeystoneDeleteUserRequest(user_id=user_id)
        return self.client.keystone_delete_user(req)
