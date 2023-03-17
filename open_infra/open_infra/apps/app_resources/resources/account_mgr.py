# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 14:27
# @Author  : Tom_zc
# @FileName: account_mgr.py
# @Software: PyCharm

from django.conf import settings

from app_resources.models import HWCloudAccount, HWCloudProjectInfo
from open_infra.libs.lib_cloud import HWCloudObs, HWCloudIAM
from open_infra.libs.lib_crypto import AESCrypt


class AccountMgr:
    _aes_crypt = AESCrypt()
    account_info_list = None

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

    @staticmethod
    def get_hw_account_from_obs():
        obs_lib = HWCloudObs(settings.OBS_AK, settings.OBS_SK, settings.OBS_URL)
        content = obs_lib.get_obs_data(settings.DOWNLOAD_BUCKET_NAME, settings.DOWNLOAD_EIP_KEY_NAME)
        return content

    @classmethod
    def get_hw_account_project_info_from_obs(cls):
        content = cls.get_hw_account_from_obs()
        cls.get_hw_project_info_from_obs(content)
        cls.handle_sensitive_data(content)
        return content

    @classmethod
    def handle_encrypt_data(cls, account_list):
        """encrypt ak and sk"""
        for account_info in account_list:
            account_info["ak"] = cls._aes_crypt.decrypt(account_info["ak"])
            account_info["sk"] = cls._aes_crypt.decrypt(account_info["sk"])

    @classmethod
    def get_hw_account_project_info_from_database(cls):
        """get all account project info from mysql"""
        account_list = list()
        account_info_list = HWCloudAccount.all()
        for account_info in account_info_list:
            account_info_dict = account_info.to_dict()
            project_info_list = HWCloudProjectInfo.get(account_info_dict["id"])
            account_info_dict["project_info"] = [{"project_id": project_info.id, "zone": project_info.zone} for
                                                 project_info in project_info_list]
            account_list.append(account_info_dict)
        return account_list

    @classmethod
    def get_decrypt_hw_account_project_info_from_database(cls):
        """first to get data from mem, if not exist, read from mysql"""
        if not cls.account_info_list:
            account_list = cls.get_hw_account_project_info_from_database()
            cls.handle_encrypt_data(account_list)
            # read data from mysql to mem
            cls.account_info_list = account_list
        return cls.account_info_list

    def get_cloud_account(self):
        """get all cloud account"""
        account_list = self.get_decrypt_hw_account_project_info_from_database()
        ret_list = list()
        for account_info in account_list:
            account_temp = dict()
            account_temp["account"] = account_info["account"]
            zone_list = [settings.ZONE_ALIAS_DICT.get(project_temp["zone"], project_temp['zone']) for project_temp in
                         account_info["project_info"]]
            account_temp["zone"] = "，".join(zone_list)
            ret_list.append(account_temp)
        return ret_list
