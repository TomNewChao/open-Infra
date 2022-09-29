# -*-coding:utf-8 -*-

import threading
import smtplib
import time
import traceback
import logging

from email.mime.text import MIMEText
from email.header import Header
from django.utils import timezone
from pytz import timezone as convert_time_zone

from alarm.models import Alarm, AlarmNotifyStrategy
from alarm.resources.alarm_module.alarm_code import AlarmCode, AlarmLevel, AlarmModule, AlarmName
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
        alarm['alarm_name'] = AlarmName.get_alarm_name_by_id(alarm_resource.get('ALARM_NAME'))
        alarm['alarm_module'] = alarm_resource.get('ALARM_MODULE')
        alarm['alarm_details'] = self._trans_str(alarm_resource.get('ALARM_CONTENT'))
        alarm['alarm_md5'] = params.get('md5')
        alarm['alarm_happen_time'] = timezone.now()
        alarm['alarm_refresh_time'] = timezone.now()
        return alarm

    def get_update_level_format(self, params):
        alarm_resource = AlarmCode.trans_to_des_by_str(params.get('alarm_id'), params.get('des_var'))
        alarm = dict()
        alarm['alarm_id'] = params.get('alarm_id')
        alarm['alarm_name'] = AlarmName.get_alarm_name_by_id(alarm_resource.get('ALARM_NAME'))
        alarm['alarm_module'] = alarm_resource.get('ALARM_MODULE')
        alarm['alarm_details'] = self._trans_str(alarm_resource.get('ALARM_CONTENT'))
        alarm['alarm_md5'] = params.get('md5')
        return alarm

    # noinspection PyMethodMayBeStatic
    def get_alarm_info(self, alam_obj):
        alarm = dict()
        alarm['id'] = alam_obj.id
        alarm['alarm_id'] = alam_obj.alarm_id
        alarm['alarm_level'] = alam_obj.alarm_level
        alarm['alarm_name'] = alam_obj.alarm_name
        alarm['alarm_module'] = alam_obj.alarm_module
        alarm['alarm_details'] = alam_obj.alarm_details
        alarm['alarm_md5'] = alam_obj.alarm_md5
        alarm['alarm_happen_time'] = alam_obj.alarm_happen_time
        alarm['alarm_refresh_time'] = alam_obj.alarm_refresh_time
        alarm["alarm_recover_time"] = timezone.now()
        return alarm

    @classmethod
    def is_alarm_level_gt_major(cls, alarm_level):
        return int(alarm_level) > int(settings.ALARM_EMAIL_DEFAULT_LEVEL)


class AlarmSMSTool(object):

    @classmethod
    def _get_sms_params(cls, alarm, alarm_type):
        if alarm_type == AlarmType.ALARM:
            alarm_detail = alarm["alarm_details"].split(r"/")[-1]
            alarm_detail = alarm_detail.replace(r"。", "")
            param_f = alarm_detail[:9] + "*" + alarm_detail[-10:]
            param_t = alarm['alarm_happen_time'].astimezone(convert_time_zone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            list_param_t = param_t.split()
            return '["{}", "{}", "{}"]'.format(param_f, list_param_t[0], list_param_t[-1])
        else:
            alarm_detail = alarm["alarm_details"].split(r"/")[-1]
            alarm_detail = alarm_detail.replace(r"。", "")
            param_f = alarm_detail[:9] + "*" + alarm_detail[-10:]
            param_t = alarm['alarm_recover_time'].astimezone(convert_time_zone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            list_param_t = param_t.split()
            return '["{}", "{}", "{}"]'.format(param_f, list_param_t[0], list_param_t[-1])

    @classmethod
    def send_sms(cls, alarm, phone_list, alarm_type):
        """send sms"""
        url = settings.ALARM_SMS_URL
        app_key = settings.ALARM_SMS_KEY
        app_secret = settings.ALARM_SMS_SECRET
        sender = settings.ALARM_SMS_SENDER
        receiver = ",".join(["+86{}".format(i) for i in phone_list])
        signature = settings.ALARM_SMS_SIGNATURE
        template_param = cls._get_sms_params(alarm, alarm_type)
        if alarm_type == AlarmType.ALARM:
            template_id = settings.ALARM_SMS_ALARM_TEMPLATE
            content = hw_send_sms(url, app_key, app_secret, sender, receiver, template_id, template_param, signature)
        else:
            template_id = settings.ALARM_SMS_RECOVER_TEMPLATE
            content = hw_send_sms(url, app_key, app_secret, sender, receiver, template_id, template_param, signature)
        logger.info("[send_sms] send sms success!send data is:{},{},{}".format(template_param, receiver, content))


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
                email_send_time = alarm['alarm_happen_time'].astimezone(convert_time_zone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
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
                        <div>告警时间：{}</div>
                        <div>解除时间：%s</div>
                    </div>
                '''.format(alarm['alarm_happen_time'].strftime('%Y-%m-%d %H:%M:%S'))
                email_send_time = alarm['alarm_recover_time'].astimezone(convert_time_zone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
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
            message['To'] = ','.join(email_receivers)
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
            logger.info("[_send_email] send email success! send data is:{}".format(email_receivers))
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

    def recover_notify_work_thread(self, alarm_info_dict):
        """the strategy to notify by using email and phone_number
        @param alarm_info_dict:
        @return:
        """
        email_list, phone_number_list = list(), list()
        try:
            alarm_name_id = AlarmName.get_alarm_name_id_by_name(alarm_info_dict["alarm_name"])
            alarm_notify_strategy_list = AlarmNotifyStrategy.objects.filter(alarm_name=alarm_name_id)
            for alarm_info in alarm_notify_strategy_list:
                alarm = Alarm.objects.filter(id=alarm_info_dict["id"])
                if alarm_info.alarm_keywords:
                    keywords_list = alarm_info.alarm_keywords.split(",")
                    for keywords in keywords_list:
                        if keywords:
                            alarm = alarm.filter(alarm_details__contains=keywords)
                if len(alarm):
                    email_list.append(alarm_info.alarm_notify.email)
                    phone_number_list.append(alarm_info.alarm_notify.phone_number)
            email_list = list(set(email_list))
            phone_number_list = list(set(phone_number_list))
            logger.info("[recover_notify_work_thread] check contact email is:{} phone_number is:{}".format(email_list,
                                                                                                           phone_number_list))
        except Exception as e:
            logger.error("[recover_notify_work_thread] find email or phone number error:{}".format(e))
        try:
            if len(email_list):
                self.alarm_email_tools.send_alarm_email(alarm_info_dict, email_list, AlarmType.RECOVER)
        except Exception as e:
            logger.error("[recover_notify_work_thread] alarm email:{}".format(e))
        try:
            if len(phone_number_list):
                self.alarm_sms_tools.send_sms(alarm_info_dict, phone_number_list, AlarmType.RECOVER)
        except Exception as e:
            logger.error("[recover_notify_work_thread] alarm sms:{}".format(e))

    def recover_notify(self, alarm_info_dict):
        """start a thread to execute func recover_notify_work_thread"""
        t = threading.Thread(target=self.recover_notify_work_thread, args=(alarm_info_dict,))
        t.start()

    def recover_alarm(self, md5_str):
        """recover alarm
        @param md5_str:
        @return:
        """
        try:
            alarm_obj = Alarm.objects.filter(alarm_md5=md5_str).filter(is_recover=False)
            if not len(alarm_obj):
                return True
            alarm_info_dict = self.alarm_server_tools.get_alarm_info(alarm_obj[0])
            Alarm.objects.filter(alarm_md5=md5_str).filter(is_recover=False).update(is_recover=True,
                                                                                    alarm_recover_time=alarm_info_dict["alarm_recover_time"])
            if not self.alarm_server_tools.is_alarm_level_gt_major(alarm_info_dict["alarm_level"]):
                self.recover_notify(alarm_info_dict)
        except Exception as e:
            logger.error("[recover_alarm] e:{}, traceback:{}".format(e, traceback.format_exc()))
        return True

    def alarm_notify_work_thread(self, alarm_info_dict):
        """the strategy to notify by using email and phone_number
        @param alarm_info_dict:
        @return:
        """
        email_list, phone_number_list = list(), list()
        try:
            alarm_name_id = AlarmName.get_alarm_name_id_by_name(alarm_info_dict["alarm_name"])
            alarm_notify_strategy_list = AlarmNotifyStrategy.objects.filter(alarm_name=alarm_name_id)
            for alarm_info in alarm_notify_strategy_list:
                alarm = Alarm.objects.filter(alarm_md5=alarm_info_dict["alarm_md5"]).filter(
                    alarm_name=alarm_info_dict["alarm_name"]).filter(is_recover=False)
                if alarm_info.alarm_keywords:
                    keywords_list = alarm_info.alarm_keywords.split(",")
                    logger.info("[alarm_notify_work_thread] alarm keywords:{}".format(keywords_list))
                    for keywords in keywords_list:
                        if keywords:
                            alarm = alarm.filter(alarm_details__contains=keywords)
                if len(alarm):
                    email_list.append(alarm_info.alarm_notify.email)
                    phone_number_list.append(alarm_info.alarm_notify.phone_number)
            email_list = list(set(email_list))
            phone_number_list = list(set(phone_number_list))
            logger.error("alarm_notify_work_thread check contact email is:{} phone_number is:{}".format(email_list,
                                                                                                        phone_number_list))
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
        """start a thread to execute func alarm_notify_work_thread"""
        t = threading.Thread(target=self.alarm_notify_work_thread, args=(alarm_info_dict,))
        t.start()

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
                is_level_gt_major = self.alarm_server_tools.is_alarm_level_gt_major(alarm_list[0].alarm_level)
                if cur_timestamps - create_timestamps >= settings.ALARM_DELAY * 60 and is_level_gt_major:
                    refresh_datetime = timezone.now()
                    Alarm.objects.filter(alarm_md5=md5_id).update(alarm_refresh_time=refresh_datetime,
                                                                  alarm_level=AlarmLevel.MAJOR)
                    dict_data = self.alarm_server_tools.get_update_level_format(params)
                    dict_data["alarm_level"] = AlarmLevel.MAJOR
                    dict_data["alarm_happen_time"] = create_datetime
                    dict_data["alarm_refresh_time"] = refresh_datetime
                    self.alarm_notify(dict_data)
                else:
                    Alarm.objects.filter(alarm_md5=md5_id).update(alarm_refresh_time=timezone.now())
            else:
                logger.info("[appear_alarm] params:{}, alarm:{}".format(params, len(alarm_list)))
                dict_data = self.alarm_server_tools.get_format_alarm(params)
                Alarm.objects.create(**dict_data)
        else:
            if len(alarm_list):
                Alarm.objects.filter(alarm_md5=md5_id).update(alarm_refresh_time=timezone.now())
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
