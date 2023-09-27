from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_superuser = models.IntegerField(default=1, verbose_name='超级管理员')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    @classmethod
    def get_user_info(cls, username):
        return cls.objects.filter(username=username).first()
