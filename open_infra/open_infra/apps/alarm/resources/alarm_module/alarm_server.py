# -*-coding:utf-8 -*-

import threading
import smtplib
import traceback
import logging
import datetime

from email.mime.text import MIMEText
from email.header import Header

from alarm.models import Alarm, AlarmEmail
from alarm.resources.alarm_module.alarm_code import AlarmCode, AlarmLevel, AlarmModule
from alarm.resources.alarm_module.constants import AlarmType
from django.conf import settings

logger = logging.getLogger("django")


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
        '''send email'''
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
    def send_alarm_email(cls, alarm, alarm_type):
        if int(alarm.get('alarm_level')) > int(settings.ALARM_EMAIL_DEFAULT_LEVEL):
            return
        alarm_email_obj_list = AlarmEmail.objects.all()
        alarm_email_list = [email_obj["email"] for email_obj in alarm_email_obj_list]
        if len(alarm_email_list) < 1:
            return
        email_conf = dict()
        email_conf['email_receivers'] = alarm_email_list
        email_conf['email_subject'] = settings.ALARM_EMAIL_SUBJECT
        email_conf['email_content'] = cls._get_alarm_email_content(alarm, alarm_type)
        threading.Thread(target=cls._send_email, args=(email_conf,)).start()


# noinspection PyMethodMayBeStatic
class AlarmServer(object):
    """AlarmServer"""

    def __init__(self):
        self.alarm_server_tools = AlarmServerTools()
        self.alarm_email_tools = AlarmEmailTool()

    def recover_alarm(self, md5_id):
        """
        recover alarm
        @param md5_id:
        @return:
        """
        # 1.start to modify mysql
        Alarm.objects.filter(alarm_md5=md5_id).filter(is_recover=False).update(is_recover=True, alarm_recover_time=datetime.datetime.now())
        # 2.send email?
        return True

    def appear_alarm(self, params):
        """
        appear alarm
        @param params: { "alarm_id": , "des_var":, "md5":, }
        @return:
        """
        md5_id = params["md5"]
        alarm_list = Alarm.objects.filter(alarm_md5=md5_id).filter(is_recover=False)
        if len(alarm_list):
            Alarm.objects.filter(alarm_md5=md5_id).update(alarm_refresh_time=datetime.datetime.now())
        else:
            logger.info("[appear_alarm] params:{}, alarm:{}".format(params, len(alarm_list)))
            dict_data = self.alarm_server_tools.get_format_alarm(params)
            Alarm.objects.create(**dict_data)
            self.alarm_email_tools.send_alarm_email(dict_data, AlarmType.ALARM)

    def send(self, params):
        """ send alarm to AlarmServer
        @param params: {'md5': md5_str} or { "alarm_id": , "des_var":, "md5":, }
        @return:
        """
        try:
            # logger.info('Receive a connect.args:{}'.format(params))
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
