import json
import logging
# Create your views here.
import re
import traceback
from datetime import datetime

from django.db import transaction

from alarm.models import AlarmNotify, AlarmNotifyStrategy
from alarm.resources.alarm_module.alarm_code import AlarmName
from alarm.resources.alarm_module.alarm_thread import batch_recover_alarm
from alarm.resources.alarm_mgr import AlarmEmailMgr, AlarmMgr
from open_infra.utils.api_error_code import ErrCode
from open_infra.utils.auth_permisson import AuthView
from open_infra.utils.common import assemble_api_result, list_param_check_and_trans

logger = logging.getLogger("django")


class AlarmView(AuthView):
    def get(self, request):
        params_dict = list_param_check_and_trans(request.GET.dict(), order_by="create_time")
        alarm_mgr = AlarmMgr()
        data = alarm_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)

    def post(self, request):
        dict_data = json.loads(request.body)
        alarm_ids = dict_data.get("alarm_ids")
        if not isinstance(alarm_ids, list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            batch_recover_alarm(alarm_ids)
        except Exception as e:
            logger.error("[AlarmView] post:{}".format(e))
            return assemble_api_result(ErrCode.INTERNAL_ERROR)
        return assemble_api_result(ErrCode.STATUS_SUCCESS)


class AlarmNameView(AuthView):
    def get(self, request):
        alarm_info = AlarmName.get_all_alarm()
        data = [{"name": name, "value": value} for value, name in alarm_info.items()]
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class AlarmNotifyView(AuthView):
    def get(self, request):
        dict_data = request.GET.dict()
        alarm_notify_id = dict_data.get("id")
        if alarm_notify_id is None:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            alarm_notify = AlarmNotify.objects.get(id=alarm_notify_id)
            dict_data = alarm_notify.to_dict()
            alarm_notify_strategy_list = AlarmNotifyStrategy.objects.filter(alarm_notify__id=alarm_notify_id)
            dict_data["alarm_name"] = [alarm_notify_strategy.alarm_name for alarm_notify_strategy in alarm_notify_strategy_list]
            alarm_info = AlarmName.get_all_alarm()
            dict_data["default_alarm_name"] = [{"name": name, "value": value} for value, name in alarm_info.items()]
            dict_data["alarm_keywords"] = alarm_notify_strategy_list[0].alarm_keywords
        except Exception as e:
            logger.error("[AlarmNotifyView] get:{}".format(e))
            return assemble_api_result(ErrCode.INTERNAL_ERROR)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=dict_data)

    def put(self, request):
        dict_data = json.loads(request.body)
        email = dict_data.get("email")
        phone_number = dict_data.get("phone")
        alarm_name_list = dict_data.get("name")
        keywords = dict_data.get("keywords")
        desc = dict_data.get("desc")
        alarm_notify_id = dict_data.get("id")
        if email and not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            logger.error("email is invalid:{}".format(email))
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if phone_number and not re.match(r"^1(3[0-9]|4[579]|5[0-3,5-9]|6[6]|7[0135678]|8[0-9]|9[89])\d{8}$",
                                         phone_number):
            logger.error("phone number invalid:{}".format(phone_number))
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if not len(email) and not len(phone_number):
            logger.error("phone number and email is empty")
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if not isinstance(alarm_name_list, list):
            logger.error("alarm name list must be list")
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        for alarm_name_id in alarm_name_list:
            if not AlarmName.get_alarm_name_by_id(alarm_name_id):
                logger.error("alarm name is invalid：{}".format(alarm_name_list))
                return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if len(desc) > 255:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            alarm_notify_obj = AlarmNotify.objects.get(id=alarm_notify_id)
            with transaction.atomic():
                AlarmNotify.objects.filter(id=alarm_notify_id).update(
                    email=email, phone_number=phone_number, desc=desc,
                )
                AlarmNotifyStrategy.objects.filter(alarm_notify_id=alarm_notify_id).delete()
                for alarm_name in alarm_name_list:
                    AlarmNotifyStrategy.objects.create(alarm_name=alarm_name, alarm_keywords=keywords,
                                                       alarm_notify=alarm_notify_obj)
        except AlarmNotify.DoesNotExist as e:
            return assemble_api_result(ErrCode.STATUS_ALARM_EMAIL_NOT_EXIST)
        except Exception as e:
            logger.info("[AlarmEmailView] {}, {}".format(e, traceback.format_exc()))
            return assemble_api_result(ErrCode.INTERNAL_ERROR)
        return assemble_api_result(ErrCode.STATUS_SUCCESS)

    def post(self, request):
        dict_data = json.loads(request.body)
        email = dict_data.get("email")
        phone_number = dict_data.get("phone")
        alarm_name_list = dict_data.get("name")
        keywords = dict_data.get("keywords")
        desc = dict_data.get("desc")
        if email and not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            logger.error("email is invalid:{}".format(email))
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if phone_number and not re.match(r"^1(3[0-9]|4[579]|5[0-3,5-9]|6[6]|7[0135678]|8[0-9]|9[89])\d{8}$",
                                         phone_number):
            logger.error("phone number invalid:{}".format(phone_number))
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if not len(email) and not len(phone_number):
            logger.error("phone number and email is empty")
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if not isinstance(alarm_name_list, list):
            logger.error("alarm name list must be list")
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        for alarm_name_id in alarm_name_list:
            if not AlarmName.get_alarm_name_by_id(alarm_name_id):
                logger.error("alarm name is invalid：{}".format(alarm_name_list))
                return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        if len(desc) > 255:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            if AlarmNotify.objects.filter(email=email).filter(phone_number=phone_number):
                return assemble_api_result(ErrCode.STATUS_ALARM_EMAIL_IS_EXIST)
        except AlarmNotify.DoesNotExist as e:
            logger.info("[AlarmEmailView] current email is not exist, could create:{}".format(email, e))
        try:
            with transaction.atomic():
                alarm_notify_obj = AlarmNotify.objects.create(email=email, phone_number=phone_number, desc=desc,
                                                              create_time=datetime.now())
                for alarm_name in alarm_name_list:
                    AlarmNotifyStrategy.objects.create(alarm_name=alarm_name, alarm_keywords=keywords,
                                                       alarm_notify=alarm_notify_obj)
        except Exception as e:
            logger.info("[AlarmEmailView] {}, {}".format(e, traceback.format_exc()))
            return assemble_api_result(ErrCode.INTERNAL_ERROR)
        return assemble_api_result(ErrCode.STATUS_SUCCESS)


class BatchAlarmNotifyView(AuthView):
    def get(self, request):
        params_dict = list_param_check_and_trans(request.GET.dict(), order_by="create_time")
        alarm_email_mgr = AlarmEmailMgr()
        data = alarm_email_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)

    def post(self, request):
        dict_data = json.loads(request.body)
        alarm_notify_ids = dict_data.get("alarm_notify_ids")
        if alarm_notify_ids is None or not isinstance(alarm_notify_ids, list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            with transaction.atomic():
                AlarmNotifyStrategy.objects.filter(alarm_notify_id__in=alarm_notify_ids)
                AlarmNotify.objects.filter(id__in=alarm_notify_ids).delete()
        except Exception as e:
            logger.info("AlarmEmailListView {}".format(e))
        return assemble_api_result(ErrCode.STATUS_SUCCESS)
