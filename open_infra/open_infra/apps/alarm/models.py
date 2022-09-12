from django.db import models

# Create your models here.
from open_infra.utils.models import BaseModel


class Alarm(BaseModel):
    alarm_id = models.IntegerField(verbose_name="报警code")
    alarm_level = models.IntegerField(verbose_name="报警级别")
    alarm_module = models.IntegerField(verbose_name="报警模块")
    alarm_name = models.CharField(max_length=64, verbose_name="报警名字")
    alarm_details = models.TextField(verbose_name="报警详细信息")
    alarm_md5 = models.CharField(max_length=64, db_index=True, verbose_name="报警信息的md5")
    is_recover = models.BooleanField(default=False, verbose_name="报警是否恢复")
    alarm_happen_time = models.DateTimeField(verbose_name="报警第一次发生时间")
    alarm_recover_time = models.DateTimeField(null=True, verbose_name="报警恢复时间")
    alarm_refresh_time = models.DateTimeField(null=True, verbose_name="报警刷新时间")

    class Meta:
        db_table = "alarm"
        verbose_name = "报警表"

    def __str__(self):
        return self.id


class AlarmEmail(BaseModel):
    email = models.EmailField(unique=True)
    desc = models.CharField(max_length=255, verbose_name="报警Email信息")
    create_time = models.DateTimeField(auto_created=True, verbose_name="创建时间")

    class Meta:
        db_table = "alarm_email"
        verbose_name = "报警邮件表"

    def __str__(self):
        return self.id
