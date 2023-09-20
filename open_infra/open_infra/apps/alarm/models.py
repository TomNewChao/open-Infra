from itertools import chain

from django.db import models

from alarm.resources.alarm_module.alarm_code import AlarmLevel, AlarmModule
from open_infra.utils.models import BaseModel


# Create your models here.
class Alarm(BaseModel):
    alarm_id = models.IntegerField(verbose_name="报警code")
    alarm_level = models.IntegerField(verbose_name="报警级别")
    alarm_module = models.IntegerField(verbose_name="报警模块")
    alarm_name = models.CharField(max_length=64, verbose_name="报警名字")
    alarm_details = models.TextField(verbose_name="报警详细信息")
    alarm_md5 = models.CharField(max_length=64, db_index=True, verbose_name="报警信息的md5")
    is_recover = models.BooleanField(default=False, verbose_name="报警是否恢复, False没有恢复/True恢复")
    alarm_happen_time = models.DateTimeField(verbose_name="报警第一次发生时间")
    alarm_recover_time = models.DateTimeField(null=True, verbose_name="报警恢复时间")
    alarm_refresh_time = models.DateTimeField(null=True, verbose_name="报警刷新时间")

    class Meta:
        db_table = "alarm"
        verbose_name = "报警表"

    def __str__(self):
        return self.id

    def to_dict(self, fields=None, exclude=None, is_relate=False):
        """to dict"""
        dict_data = dict()
        for f in chain(self._meta.concrete_fields, self._meta.many_to_many):
            value = f.value_from_object(self)
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if isinstance(f, models.ManyToManyField):
                if is_relate is False:
                    continue
                value = [i.to_dict() for i in value] if self.pk else None
            if isinstance(f, models.DateTimeField):
                value = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
            if f.name == "alarm_level":
                value = AlarmLevel.CN_ALARM_LEVEL.get(value)
            if f.name == "alarm_module":
                value = AlarmModule.CN_ALARM_MODULE.get(value)
            if f.name == "is_recover":
                value = "是" if value else "否"
            dict_data[f.name] = value
        return dict_data


class AlarmNotify(BaseModel):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, verbose_name="报警手机号")
    desc = models.CharField(max_length=255, verbose_name="报警Email信息")
    create_time = models.DateTimeField(auto_created=True, verbose_name="创建时间")

    class Meta:
        db_table = "alarm_notify"
        verbose_name = "报警通知"

    def __str__(self):
        return self.id


class AlarmNotifyStrategy(BaseModel):
    alarm_name = models.IntegerField(verbose_name="报警名字id")
    alarm_keywords = models.CharField(max_length=255, verbose_name="报警详细信息关键字")
    alarm_notify = models.ForeignKey(AlarmNotify, verbose_name="报警通知", on_delete=models.CASCADE)

    class Meta:
        db_table = "alarm_notify_strategy"
        verbose_name = "报警通知策略"

    def __str__(self):
        return self.id
