# -*- coding: utf-8 -*-
# @Time    : 2023/3/16 17:01
# @Author  : Tom_zc
# @FileName: constants.py
# @Software: PyCharm
from open_infra.utils.common import BaseStatus


class Community(BaseStatus):
    """The all community"""
    INFRA = (0, "infra")
    MINDSPORE = (1, "mindspore")
    OPENGUASS = (2, "opengauss")
    OPENEULER = (3, "openeuler")
    OPENLOOKENG = (4, "openlookeng")

    @classmethod
    def is_in_community(cls, community):
        """judge community is in this community"""
        dict_data = cls.get_comment_status()
        if community in dict_data.keys():
            return True
        else:
            return False


class ObsInteractComment(object):
    """The Obs Interact of comment"""
    error = "The internal service is abnormal, Please contact the warehouse administrator."
    welcome = """Hi ***{}***, welcome to the Open-Infra-Ops Community.\nI'm the Bot here serving you.Thank you for submitting the obs request.\nApplication check result: ***{}***.\nDetail: {}"""
    lgtm = """Hi ***{}***, Thank you for your application. The information about your application has been sent to you by email, please check it carefully."""
    valid_lgtm = "Hi, lgtm should be confirmed by the repository administrator: {}."
    check_upload_false = """Hi ***{}***,Unfortunately, the file you uploaded did not pass the inspection, And the reason for the failure to pass the inspection:\n{}"""
    check_upload_ok = """Hi ***{}***,Congratulations, the uploaded file passed the inspection successfully, this PR request will be closed automatically"""
