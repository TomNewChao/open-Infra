from itertools import chain

from clouds_tools.resources.constants import HWCloudEipStatus, HWCloudEipType
from open_infra.utils.models import BaseModel
from django.db import models


class HWCloudAccount(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户name")
    ak = models.CharField(max_length=255, verbose_name="华为云账户的ak")
    sk = models.CharField(max_length=255, verbose_name="华为云账户的sk")

    class Meta:
        db_table = "hw_cloud_account"
        verbose_name = "华为云账户"

    def __str__(self):
        return self.account


class HWCloudProjectInfo(BaseModel):
    id = models.CharField(max_length=64, primary_key=True, verbose_name="华为云项目id")
    zone = models.CharField(max_length=32, verbose_name="华为云项目zone")
    account = models.ForeignKey(HWCloudAccount, on_delete=models.CASCADE, verbose_name="外键，关联华为云的账户id")

    class Meta:
        db_table = "hw_cloud_project_info"
        verbose_name = "华为云项目信息"

    def __str__(self):
        return str(self.id)


class HWCloudEipInfo(BaseModel):
    id = models.CharField(max_length=64, primary_key=True, verbose_name="华为云eip的id")
    eip = models.GenericIPAddressField()
    eip_status = models.IntegerField(null=True, verbose_name="华为云eip的status")
    eip_type = models.IntegerField(null=True, verbose_name="华为云eip的type")
    eip_zone = models.CharField(max_length=64, null=True, verbose_name="华为云eip归属区域")
    bandwidth_id = models.CharField(max_length=64, null=True, verbose_name="华为云的带宽id")
    bandwidth_name = models.CharField(max_length=64, null=True, verbose_name="华为云的带宽name")
    bandwidth_size = models.IntegerField(null=True, verbose_name="华为云的带宽size")
    example_id = models.CharField(max_length=64, null=True, verbose_name="实例id")
    example_name = models.CharField(max_length=64, null=True, verbose_name="实例name")
    example_type = models.CharField(max_length=32, null=True, verbose_name="实例type")
    create_time = models.DateTimeField(verbose_name="创建时间")
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")  # not use FK, for refresh data

    def to_dict(self, fields=None, exclude=None, is_relate=False):
        """
        转dict
        :return:
        """
        dict_data = dict()
        eip_status_dict = HWCloudEipStatus.get_status_comment()
        eip_type_dict = HWCloudEipType.get_status_comment()
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
            if f.name == "eip_status":
                value = eip_status_dict[value]
            if f.name == "eip_type":
                value = eip_type_dict[value]
            dict_data[f.name] = value
        return dict_data

    class Meta:
        db_table = "hw_cloud_eip_info"
        verbose_name = "华为云eip信息"

    def __str__(self):
        return str(self.id)
