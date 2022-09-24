# -*- coding: utf-8 -*-
# @Time    : 2022/9/24 15:48
# @Author  : Tom_zc
# @FileName: sms_lib.py
# @Software: PyCharm

import time
import uuid
import hashlib
import base64
import requests


def build_wsse_header(app_key, app_secret):
    now = time.strftime('%Y-%m-%dT%H:%M:%SZ')
    nonce = str(uuid.uuid4()).replace('-', '')
    digest = hashlib.sha256((nonce + now + app_secret).encode()).hexdigest()
    digest_base64 = base64.b64encode(digest.encode()).decode()
    return 'UsernameToken Username="{}",PasswordDigest="{}",Nonce="{}",Created="{}"'.format(app_key, digest_base64,
                                                                                            nonce,
                                                                                            now)


def hw_send_sms(url, app_key, app_secret, sender, receiver, template_id, template_param, signature):
    """
    @param url: 应用url
    @param app_key: 应用公钥
    @param app_secret: 应用秘钥
    @param sender: 发送者
    @param receiver: 接受者
    @param template_id: 模板id
    @param template_param: 模板参数
    @param signature:  使用国内短信通用模板时,必须填写签名名称
    @return:
    """
    header = {'Authorization': 'WSSE realm="SDP",profile="UsernameToken",type="Appkey"',
              'X-WSSE': build_wsse_header(app_key, app_secret)}
    form_data = {
        'from': sender,
        'to': receiver,
        'templateId': template_id,
        'templateParas': template_param,
        'statusCallback': '',
        'signature': signature
    }
    r = requests.post(url, data=form_data, headers=header, verify=False)
    if not str(r.status_code).startswith("2"):
        raise Exception("[send_sms] send sms failed:{}, content:{}".format(r.status_code, r.text))
