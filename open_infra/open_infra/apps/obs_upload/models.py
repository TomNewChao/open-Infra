# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
from open_infra.utils.models import BaseModel


class HWColudObsInteract(BaseModel):
    username = models.CharField(max_length=64, verbose_name="华为云IAM用户")
    community = models.CharField(max_length=16, verbose_name="社区")
    user_id = models.CharField(max_length=32, verbose_name="用户id")
    password = models.CharField(max_length=64, verbose_name="用户密码")
    is_delete = models.BooleanField(default=False, verbose_name="软删除")

    class Meta:
        db_table = "hw_cloud_obs_interact"
        verbose_name = "华为云对象上传系统"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)
