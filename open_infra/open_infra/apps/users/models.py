from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    is_superuser = models.IntegerField(default=1, verbose_name='超级管理员')

    class Meta:
        db_table = 'users_table'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
