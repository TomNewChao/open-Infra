# -*- coding: utf-8 -*-
# @Time    : 2022/7/21 15:21
# @Author  : Tom_zc
# @FileName: obs_utils.py
# @Software: PyCharm

import json
from obs import ObsClient
from logging import getLogger

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

    # def get_obs_data(self, download_bucket, download_key):
    #     content = str()
    #     resp = self.obs_client.getObject(download_bucket, download_key, loadStreamInMemory=False)
    #     if resp.status < 300:
    #         while True:
    #             chunk = resp.body.response.read(65536)
    #             if not chunk:
    #                 break
    #             content = "{}{}".format(content, chunk.decode("utf-8"))
    #         resp.body.response.close()
    #     elif resp.errorCode == "NoSuchKey":
    #         logger.info("Key:{} is not exist, need to create".format(download_key))
    #     else:
    #         logger.error('errorCode:', resp.errorCode)
    #         logger.error('errorMessage:', resp.errorMessage)
    #         raise Exception("get object failed：{}....".format(download_key))
    #     return content

    def get_obs_data(self, download_bucket, download_key):
        with open("/root/yaml/collect_elastic_public_ip.yaml", "r") as f:
            return f.read()
