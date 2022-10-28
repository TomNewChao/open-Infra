# -*- coding: utf-8 -*-
# @Time    : 2022/10/25 16:21
# @Author  : Tom_zc
# @FileName: lib_email.py
# @Software: PyCharm
import smtplib
from django.conf import settings


class EmailBaseLib(object):
    sender_email = settings.EMAIL_SENDER_EMAIL
    sender_name = settings.EMAIL_SENDER_NAME
    server_address = settings.EMAIL_SENDER_SERVER
    server_port = int(settings.EMAIL_SENDER_PORT)
    login_username = settings.EMAIL_USERNAME
    login_password = settings.EMAIL_PWD
    is_ssl = settings.EMAIL_IS_SSL

    @classmethod
    def send_email(cls, email_receivers, message):
        """send eamil"""
        if not cls.is_ssl:
            smt_obj = smtplib.SMTP(cls.server_address, port=int(cls.server_port))
            smt_obj.login(cls.login_username, cls.login_password)
            smt_obj.starttls()
            smt_obj.sendmail(cls.sender_email, email_receivers, message.as_string())
        else:
            smt_obj = smtplib.SMTP_SSL(cls.server_address, port=int(cls.server_port))
            smt_obj.login(settings.ALARM_EMAIL_USERNAME, settings.ALARM_EMAIL_PWD)
            smt_obj.sendmail(cls.sender_email, email_receivers, message.as_string())
