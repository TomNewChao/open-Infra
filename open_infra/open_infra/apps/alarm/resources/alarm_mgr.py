import logging
from alarm.models import Alarm, AlarmNotify, AlarmNotifyStrategy
from alarm.resources.alarm_module.alarm_code import AlarmName, AlarmLevel
from open_infra.utils.common import get_suitable_range

logger = logging.getLogger("django")


# noinspection PyMethodMayBeStatic
class AlarmEmailMgr:

    def list(self, kwargs):
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        if filter_name and filter_name == "email":
            email_list = AlarmNotify.objects.filter(email__contains=filter_value)
        elif filter_name and filter_name == "phone_number":
            email_list = AlarmNotify.objects.filter(phone_number__contains=filter_value)
        else:
            email_list = AlarmNotify.objects.all()
        total = len(email_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "create_time"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        email_list = email_list.order_by(order_by)
        task_list = [task.to_dict() for task in email_list[slice_obj]]
        dict_data = dict()
        alarm_notify_strategy_list = AlarmNotifyStrategy.objects.filter(alarm_notify__id__in=[task["id"] for task in task_list])
        for alarm_notify_strategy in alarm_notify_strategy_list:
            alarm_name = AlarmName.get_alarm_name_by_id(alarm_notify_strategy.alarm_name)
            if alarm_notify_strategy.alarm_notify.id not in dict_data.keys():
                dict_data[alarm_notify_strategy.alarm_notify.id] = {"alarm_name": [alarm_name], "alarm_keywords": alarm_notify_strategy.alarm_keywords}
            else:
                dict_data[alarm_notify_strategy.alarm_notify.id]["alarm_name"].append(alarm_name)
        for task in task_list:
            task["alarm_name"] = "，".join(dict_data[task["id"]]["alarm_name"])
            task["alarm_keywords"] = dict_data[task["id"]]["alarm_keywords"]
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": task_list
        }
        return res


# noinspection PyMethodMayBeStatic
class AlarmMgr:
    def list(self, kwargs):
        page, size = kwargs['page'], kwargs['size']
        order_type, order_by = kwargs.get("order_type"), kwargs.get("order_by")
        filter_name = kwargs.get("filter_name")
        filter_value = kwargs.get("filter_value")
        if filter_name and filter_name == "alarm_name":
            alarm_list = Alarm.objects.filter(alarm_name__contains=filter_value).filter(is_recover=False)
        elif filter_name and filter_name == "alarm_level":
            filter_value = AlarmLevel.get_alarm_level_id_by_name(filter_value)
            alarm_list = Alarm.objects.filter(alarm_level=filter_value).filter(is_recover=False)
        elif filter_name and filter_name == "alarm_details":
            alarm_list = Alarm.objects.filter(alarm_details__contains=filter_value).filter(is_recover=False)
        else:
            alarm_list = Alarm.objects.all().filter(is_recover=False)
        total = len(alarm_list)
        page, slice_obj = get_suitable_range(total, page, size)
        order_by = order_by if order_by else "alarm_refresh_time"
        order_type = order_type if order_type else 0
        if order_type != 0:
            order_by = "-" + order_by
        eip_list = alarm_list.order_by(order_by)
        task_list = [task.to_dict() for task in eip_list[slice_obj]]
        res = {
            "size": size,
            "page": page,
            "total": total,
            "data": task_list
        }
        return res
