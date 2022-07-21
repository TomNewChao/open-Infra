from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractUser


# 创建user用户的模型类，用于生成Mysql表
class User(AbstractUser):
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name="邮件激活")
    is_superuser = models.IntegerField(default=1, verbose_name='超级管理员', )
    is_staff = models.IntegerField(default=1, verbose_name='商家店员', )

    # 生成的表
    class Meta:
        db_table = 'users_tb'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
