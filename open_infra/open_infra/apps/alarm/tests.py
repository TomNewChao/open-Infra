import smtplib
import time
import uuid
import hashlib
import base64
import requests
from email.header import Header
from email.mime.text import MIMEText


# from django.test import TestCase
# Create your tests here.


def test_email():
    email_subject = "hello tom"
    email_content = "hello tom, I am TOm"
    email_receivers = ["tom_toworld@163.com"]
    sender_email = "infra@lists.osinfra.cn"
    sender_name = "infra"
    # server_address = "smtp.qq.com"
    server_address = "lists.osinfra.cn"
    server_port = int(465)
    message = MIMEText(email_content, 'html', 'utf-8')
    message['From'] = r'{0} <{1}>'.format(sender_name, sender_email)
    message['To'] = ';'.join(email_receivers)
    message['Subject'] = Header(email_subject, 'utf-8')
    smt_obj = smtplib.SMTP_SSL(server_address, port=int(server_port))
    smt_obj.login("", "")
    smt_obj.sendmail(sender_email, email_receivers, message.as_string())


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
    @param url:
    @param app_key:
    @param app_secret:
    @param sender:
    @param receiver:
    @param template_id:
    @param template_param:
    @param signature:
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


ALARM_SMS_URL = "https://smsapi.cn-south-1.myhuaweicloud.com:443/sms/batchSendSms/v1"  # guangzhou
ALARM_SMS_KEY = ""
ALARM_SMS_SECRET = ""
ALARM_SMS_SENDER = ""
ALARM_SMS_TEMPLATE = ""
ALARM_SMS_SIGNATURE = ""


def test_phone_number():
    hw_send_sms(ALARM_SMS_URL,
                ALARM_SMS_KEY,
                ALARM_SMS_SECRET,
                ALARM_SMS_SENDER,
                "+8618227751270,+8617603095488",
                ALARM_SMS_TEMPLATE,
                '["1", "2"]',
                ALARM_SMS_SIGNATURE)


if __name__ == '__main__':
    # test_email()
    # test_phone_number()
    pass
