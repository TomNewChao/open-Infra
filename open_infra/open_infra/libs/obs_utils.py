# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:21
# @Author  : Tom_zc
# @FileName: obs_utils.py
# @Software: PyCharm

import json

from obs import ObsClient
from logging import getLogger
from django.conf import settings

from open_infra.utils.common import convert_yaml
from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkiam.v3.region.iam_region import IamRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkiam.v3 import IamClient, KeystoneListProjectsRequest
from huaweicloudsdkcore.http.http_config import HttpConfig

logger = getLogger("django")


class ObsLib(object):
    def __init__(self, ak=None, sk=None, url=None, obs_client=None):
        if obs_client is None:
            self.obs_client = ObsClient(access_key_id=ak,
                                        secret_access_key=sk,
                                        server=url)
        else:
            self.obs_client = obs_client

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


class HWCloudIAM(object):
    @staticmethod
    def get_iam_config():
        config = HttpConfig.get_default_config()
        config.ignore_ssl_verification = True
        config.retry_times = 1
        config.timeout = (180, 180)
        return config

    @classmethod
    def get_project_zone(cls, ak, sk):
        list_data = list()
        try:
            credentials = GlobalCredentials(ak, sk)
            config = cls.get_iam_config()
            client = IamClient.new_builder().with_http_config(config) \
                .with_credentials(credentials) \
                .with_region(IamRegion.value_of("ap-southeast-1")) \
                .build()
            request = KeystoneListProjectsRequest()
            response = client.keystone_list_projects(request)
            for info in response.projects:
                if info.name in settings.IGNORE_ZONE:
                    continue
                list_data.append({"zone": info.name, "project_id": info.id})
            logger.info("[get_project_zone] collect project total:{}".format(len(list_data)))
            return list_data
        except exceptions.ClientRequestException as e:
            logger.error(
                "ak:{}, sk:{} get project zone failed:{},{},{},{}".format(ak[:5], sk[:5], e.status_code, e.request_id,
                                                                          e.error_code, e.error_msg))
            return list_data
