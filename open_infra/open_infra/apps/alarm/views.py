import json
import logging
# Create your views here.
import traceback
from datetime import datetime
from alarm.models import AlarmEmail, Alarm
from alarm.resources.alarm_module.alarm_thread import AlarmGlobalConfig
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
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data)

    def post(self, request):
        dict_data = json.loads(request.body)
        alarm_ids = dict_data.get("alarm_ids")
        if not isinstance(alarm_ids, list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            Alarm.objects.filter(alarm_md5__in=alarm_ids).update(is_recover=True, alarm_recover_time=datetime.now())
            for alarm_str in alarm_ids:
                if alarm_str in AlarmGlobalConfig.ALARM_STATUS_DICT.keys():
                    del AlarmGlobalConfig.ALARM_STATUS_DICT[alarm_str]
                if alarm_str in AlarmGlobalConfig.RETRY_NEED_TASK_DICT.keys():
                    del AlarmGlobalConfig.RETRY_NEED_TASK_DICT[alarm_str]
        except Exception as e:
            return assemble_api_result(ErrCode.INTERNAL_ERROR)
        return assemble_api_result(ErrCode.STATUS_SUCCESS)


class AlarmEmailView(AuthView):
    def get(self, request):
        dict_data = request.GET
        email_id = dict_data.get("id")
        if email_id is None:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            alarm_email_obj = AlarmEmail.objects.get(id=email_id)
        except AlarmEmail.DoesNotExist as e:
            return assemble_api_result(ErrCode.STATUS_ALARM_EMAIL_NOT_EXIST)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, alarm_email_obj.to_dict())

    def post(self, request):
        dict_data = json.loads(request.body)
        email = dict_data.get("email")
        desc = dict_data.get("desc")
        if not email or len(desc) > 255:
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            if AlarmEmail.objects.get(email=email):
                return assemble_api_result(ErrCode.STATUS_ALARM_EMAIL_IS_EXIST)
        except AlarmEmail.DoesNotExist as e:
            logger.info("[AlarmEmailView] current email is not exist, could create:{}".format(email, e))
        try:
            AlarmEmail.objects.create(email=email, desc=desc, create_time=datetime.now())
        except Exception as e:
            logger.info("[AlarmEmailView] {}, {}".format(e, traceback.format_exc()))
            return assemble_api_result(ErrCode.INTERNAL_ERROR)
        return assemble_api_result(ErrCode.STATUS_SUCCESS)


class AlarmEmailListView(AuthView):
    def get(self, request):
        params_dict = list_param_check_and_trans(request.GET.dict(), order_by="create_time")
        alarm_email_mgr = AlarmEmailMgr()
        data = alarm_email_mgr.list(params_dict)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)

    def post(self, request):
        dict_data = json.loads(request.body)
        email_list = dict_data.get("email_list")

        if email_list is None or not isinstance(email_list, list):
            return assemble_api_result(ErrCode.STATUS_PARAMETER_ERROR)
        try:
            AlarmEmail.objects.filter(email__in=email_list).delete()
        except AlarmEmail.DoesNotExist as e:
            logger.info("AlarmEmailListView {}".format(e))
        return assemble_api_result(ErrCode.STATUS_SUCCESS)
