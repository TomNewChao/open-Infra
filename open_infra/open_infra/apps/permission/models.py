from itertools import chain
from django.db import models
from open_infra.utils.models import BaseModel


class KubeConfigInfo(BaseModel):
    username = models.CharField(max_length=64, verbose_name="用户名称")
    email = models.EmailField()
    role = models.CharField(max_length=16, verbose_name="角色")
    service_name = models.CharField(max_length=128, null=True, verbose_name="服务名称")
    create_time = models.DateTimeField(verbose_name="创建时间")
    review_time = models.DateTimeField(null=True, verbose_name="审核时间")
    modify_time = models.DateTimeField(null=True, verbose_name="修改时间")
    expired_time = models.IntegerField(null=True, verbose_name="过期间隔时间,单位:day")
    send_ok = models.BooleanField(null=True, verbose_name="邮件发送ok")

    def to_dict(self, fields=None, exclude=None, is_relate=False):
        """
        转dict
        :return:
        """
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
            if f.name == "send_ok":
                value = "是" if value else "否"
            dict_data[f.name] = value
        return dict_data

    class Meta:
        db_table = "kubeconfig_info"
        verbose_name = "kubeconfig_info表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id

