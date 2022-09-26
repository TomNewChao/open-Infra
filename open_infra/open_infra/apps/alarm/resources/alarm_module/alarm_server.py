# -*-coding:utf-8 -*-

import threading
import smtplib
import time
import traceback
import logging
import datetime

from email.mime.text import MIMEText
from email.header import Header

from alarm.models import Alarm, AlarmNotifyStrategy
from alarm.resources.alarm_module.alarm_code import AlarmCode, AlarmLevel, AlarmModule
from alarm.resources.alarm_module.constants import AlarmType
from django.conf import settings

from open_infra.libs.sms_lib import hw_send_sms

logger = logging.getLogger("django")


class AlarmServerConfig:
    AlarmBaseCode = 20


class AlarmServerTools:
    @staticmethod
    def _trans_str(str_val):
        str_val = str_val.replace("\\", "\\\\")
        str_val = str_val.replace("'", "\\'")
        str_val = str_val.replace('"', '\\"')
        return str_val

    def get_format_alarm(self, params):
        alarm_resource = AlarmCode.trans_to_des_by_str(params.get('alarm_id'), params.get('des_var'))
        alarm = dict()
        alarm['alarm_id'] = params.get('alarm_id')
        alarm['alarm_level'] = alarm_resource.get('ALARM_LEVEL')
        alarm['alarm_name'] = alarm_resource.get('ALARM_NAME')
        alarm['alarm_module'] = alarm_resource.get('ALARM_MODULE')
        alarm['alarm_details'] = self._trans_str(alarm_resource.get('ALARM_CONTENT'))
        alarm['alarm_md5'] = params.get('md5')
        cur_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        alarm['alarm_happen_time'] = cur_date
        alarm['alarm_refresh_time'] = cur_date
        return alarm

    def get_update_level_format(self, params):
        alarm_resource = AlarmCode.trans_to_des_by_str(params.get('alarm_id'), params.get('des_var'))
        alarm = dict()
        alarm['alarm_id'] = params.get('alarm_id')
        alarm['alarm_name'] = alarm_resource.get('ALARM_NAME')
        alarm['alarm_module'] = alarm_resource.get('ALARM_MODULE')
        alarm['alarm_details'] = self._trans_str(alarm_resource.get('ALARM_CONTENT'))
        alarm['alarm_md5'] = params.get('md5')
        return alarm


class AlarmSMSTool(object):

    @classmethod
    def _get_sms_params(cls, alarm):
        params_list = list()
        params_list.append(alarm.get('alarm_name'))
        params_list.append(AlarmModule.get_module_desc_by_id(alarm.get('alarm_module')))
        params_list.append(AlarmLevel.CN_ALARM_LEVEL.get(alarm.get('alarm_level')))
        params_list.append(alarm.get('alarm_details'))
        return params_list

    @classmethod
    def send_sms(cls, alarm, phone_list, alarm_type):
        """send sms"""
        url = settings.ALARM_SMS_URL
        app_key = settings.ALARM_SMS_KEY
        app_secret = settings.ALARM_SMS_SECRET
        sender = settings.ALARM_SMS_SENDER
        receiver = ",".join(["+86{}".format(i) for i in phone_list])
        if alarm_type == AlarmType.ALARM:
            template_id = settings.ALARM_SMS_TEMPLATE
            template_param = cls._get_sms_params(alarm)
            signature = settings.ALARM_SMS_SIGNATURE
            hw_send_sms(url, app_key, app_secret, sender, receiver, template_id, template_param, signature)
        else:
            template_id = settings.ALARM_SMS_TEMPLATE
            template_param = cls._get_sms_params(alarm)
            signature = settings.ALARM_SMS_SIGNATURE
            hw_send_sms(url, app_key, app_secret, sender, receiver, template_id, template_param, signature)


class AlarmEmailTool(object):

    @classmethod
    def _get_alarm_email_content(cls, alarm, alarm_type):
        """
        根据类型返回对应模板
        :param alarm:
        :param alarm_type:上报/解除
        :return:
        """
        try:
            if alarm_type == AlarmType.ALARM:
                email_content_temp = '''
                    <div style="margin:10px 20px;font-size:12px;font-family:SimSun;">
                        <div>尊敬的用户：</div>
                        <div>您好！</div>
                        <div>此告警邮件由系统自动发出，无需回复。</div></br>
                        <div>告警详情如下：</div>
                        <div>————————————————————————————————————————————————————————————————————————————</div>
                        <div>告警名：%s</div>
                        <div>告警模块：%s</div>
                        <div>告警级别：<font style="font-weight:bold;color:%s">%s</font></div>
                        <div>告警内容：%s</div>
                        <div>告警时间：%s</div>
                    </div>
                '''
                email_send_time = alarm.get('alarm_happen_time')
            elif alarm_type == AlarmType.RECOVER:
                email_content_temp = '''
                    <div style="margin:10px 20px;font-size:12px;font-family:SimSun;">
                        <div>尊敬的用户：</div>
                        <div>您好！</div>
                        <div>此解除告警邮件由系统自动发出，无需回复。</div></br>
                        <div>解除告警详情如下：</div>
                        <div>————————————————————————————————————————————————————————————————————————————</div>
                        <div>告警名：%s</div>
                        <div>告警模块：%s</div>
                        <div>告警级别：<font style="font-weight:bold;color:%s">%s</font></div>
                        <div>告警内容：%s</div>
                        <div>解除时间：%s</div>
                    </div>
                '''
                email_send_time = alarm.get('alarm_recover_time')
            else:
                raise TypeError('alarm type {} is unknown.'.format(alarm_type))
            email_content = email_content_temp % (alarm.get('alarm_name'),
                                                  AlarmModule.get_module_desc_by_id(alarm.get('alarm_module')),
                                                  AlarmLevel.ALARM_LEVEL_COLOR.get(alarm.get('alarm_level')),
                                                  AlarmLevel.CN_ALARM_LEVEL.get(alarm.get('alarm_level')),
                                                  alarm.get('alarm_details'),
                                                  email_send_time)
            return email_content
        except Exception as e:
            logger.error('format email content failed,e=%s,t=%s', e.args[0], traceback.format_exc())

    @classmethod
    def _send_email(cls, email_conf):
        """send email"""
        try:
            email_subject = email_conf.get('email_subject')
            email_content = email_conf.get('email_content')
            email_receivers = email_conf.get('email_receivers')
            sender_email = settings.ALARM_EMAIL_SENDER_EMAIL
            sender_name = settings.ALARM_EMAIL_SENDER_NAME
            server_address = settings.ALARM_EMAIL_SENDER_SERVER
            server_port = int(settings.ALARM_EMAIL_SENDER_PORT)
            message = MIMEText(email_content, 'html', 'utf-8')
            message['From'] = r'{0} <{1}>'.format(sender_name, sender_email)
            message['To'] = ';'.join(email_receivers)
            message['Subject'] = Header(email_subject, 'utf-8')
            if not settings.IS_SSL:
                smt_obj = smtplib.SMTP(server_address, port=int(server_port))
                smt_obj.login(settings.ALARM_EMAIL_USERNAME, settings.ALARM_EMAIL_PWD)
                smt_obj.starttls()
                smt_obj.sendmail(sender_email, email_receivers, message.as_string())
            else:
                smt_obj = smtplib.SMTP_SSL(server_address, port=int(server_port))
                smt_obj.login(settings.ALARM_EMAIL_USERNAME, settings.ALARM_EMAIL_PWD)
                smt_obj.sendmail(sender_email, email_receivers, message.as_string())
            logger.info("[_send_email] send email success!")
        except Exception as e:
            logger.error('send email failed,e=%s,t=%s', e.args[0], traceback.format_exc())

    @classmethod
    def send_alarm_email(cls, alarm, email_list, alarm_type):
        email_conf = dict()
        email_conf['email_receivers'] = email_list
        email_conf['email_subject'] = settings.ALARM_EMAIL_SUBJECT
        email_conf['email_content'] = cls._get_alarm_email_content(alarm, alarm_type)
        cls._send_email(email_conf)


# noinspection PyMethodMayBeStatic
class AlarmServer(object):
    """AlarmServer"""

    def __init__(self):
        self.alarm_server_tools = AlarmServerTools()
        self.alarm_email_tools = AlarmEmailTool()
        self.alarm_sms_tools = AlarmSMSTool()

    def recover_alarm(self, md5_id):
        """
        recover alarm
        @param md5_id:
        @return:
        """
        # 1.start to modify mysql
        Alarm.objects.filter(alarm_md5=md5_id).filter(is_recover=False).update(is_recover=True,
                                                                               alarm_recover_time=datetime.datetime.now())
        # 2.send email?
        return True

    def alarm_notify_work_thread(self, alarm_info_dict):
        email_list, phone_number_list = list(), list()
        try:
            if alarm_info_dict["alarm_id"] < AlarmServerConfig.AlarmBaseCode:
                # 下面的可能有多条数据
                alarm_notify_strategy_list = AlarmNotifyStrategy.objects.filter(alarm_name=alarm_info_dict["alarm_name"])
                for alarm_info in alarm_notify_strategy_list:
                    alarm = Alarm.objects.filter(alarm_md5=alarm_info_dict["alarm_md5"]).filter(
                        alarm_name=alarm_info_dict["alarm_name"])
                    if alarm_info.keywords:
                        alarm = alarm.filter(alarm_details__contains=alarm_info.keywords)
                    if len(alarm):
                        email_list.append(alarm_info.alarm_notify.email)
                        phone_number_list.append(alarm_info.alarm_notify.phone_number)
            else:
                alarm_notify_list = AlarmNotifyStrategy.objects.filter(
                    alarm_name=alarm_info_dict["alarm_name"]).values("alarm_notify__email", "alarm_notify__phone_number")
                for alarm_notify_info in alarm_notify_list:
                    if alarm_notify_info.alarm_notify__email:
                        email_list.append(alarm_notify_info.alarm_notify__email)
                    if alarm_notify_info.alarm_notify__phone_number:
                        phone_number_list.append(alarm_notify_info.alarm_notify__phone_number)
            email_list = list(set(email_list))
            phone_number_list = list(set(phone_number_list))
        except Exception as e:
            logger.error("[alarm_notify_work_thread] find email or phone number error:{}".format(e))
        try:
            if len(email_list):
                self.alarm_email_tools.send_alarm_email(alarm_info_dict, email_list, AlarmType.ALARM)
        except Exception as e:
            logger.error("[alarm_notify_work_thread] alarm email:{}".format(e))
        try:
            if len(phone_number_list):
                self.alarm_sms_tools.send_sms(alarm_info_dict, phone_number_list, AlarmType.ALARM)
        except Exception as e:
            logger.error("[alarm_notify_work_thread] alarm sms:{}".format(e))

    def alarm_notify(self, alarm_info_dict):
        if int(alarm_info_dict.get('alarm_level')) > int(settings.ALARM_EMAIL_DEFAULT_LEVEL):
            return
        threading.Thread(target=self.alarm_notify_work_thread, args=(alarm_info_dict,)).start()

    def appear_alarm(self, params):
        """
        appear alarm
        @param params: { "alarm_id": , "des_var":, "md5":, }
        @return:
        """
        md5_id = params["md5"]
        alarm_id = params["alarm_id"]
        alarm_list = Alarm.objects.filter(alarm_md5=md5_id).filter(is_recover=False)
        # alarm_id lt 20, it is monitor, It is created over 30 minutes, it is needed to modify the alarm level
        if alarm_id < AlarmServerConfig.AlarmBaseCode:
            if len(alarm_list):
                cur_timestamps = int(time.time())
                create_datetime = alarm_list[0].alarm_happen_time
                create_timestamps = int(time.mktime(create_datetime.timetuple()))
                if cur_timestamps - create_timestamps >= settings.ALARM_DELAY * 60:
                    refresh_datetime = datetime.datetime.now()
                    Alarm.objects.filter(alarm_md5=md5_id).update(alarm_refresh_time=refresh_datetime,
                                                                  alarm_level=AlarmLevel.MAJOR)
                    dict_data = self.alarm_server_tools.get_update_level_format(params)
                    dict_data["alarm_level"] = AlarmLevel.MAJOR
                    dict_data["alarm_happen_time"] = create_timestamps
                    dict_data["alarm_refresh_time"] = refresh_datetime
                    self.alarm_notify(dict_data)
                else:
                    Alarm.objects.filter(alarm_md5=md5_id).update(alarm_refresh_time=datetime.datetime.now())
            else:
                logger.info("[appear_alarm] params:{}, alarm:{}".format(params, len(alarm_list)))
                dict_data = self.alarm_server_tools.get_format_alarm(params)
                Alarm.objects.create(**dict_data)
        else:
            if len(alarm_list):
                Alarm.objects.filter(alarm_md5=md5_id).update(alarm_refresh_time=datetime.datetime.now())
            else:
                logger.info("[appear_alarm] params:{}, alarm:{}".format(params, len(alarm_list)))
                dict_data = self.alarm_server_tools.get_format_alarm(params)
                Alarm.objects.create(**dict_data)
                self.alarm_notify(dict_data)

    def send(self, params):
        """ send alarm to AlarmServer
        @param params: {'md5': md5_str} or { "alarm_id": , "des_var":, "md5":, }
        @return:
        """
        try:
            if not isinstance(params, dict):
                raise TypeError(type(params))
            if params.get('alarm_id', None):
                self.appear_alarm(params)
            elif params.get('md5', None):
                self.recover_alarm(params.get('md5'))
            else:
                raise Exception('alarm param incorrect.')
            return True
        except Exception as e:
            logger.exception('Alarm server exception.{}'.format(e))
            return False
