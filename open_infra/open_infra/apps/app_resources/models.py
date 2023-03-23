# -*- coding: utf-8 -*-
# Create your models here.
from itertools import chain

from django.db.models import Count

from app_resources.resources.constants import HWCloudEipStatus, HWCloudEipType
from open_infra.utils.models import BaseModel
from django.db import models
from logging import getLogger
logger = getLogger("django")


class HWCloudAccount(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户name")
    ak = models.CharField(max_length=255, verbose_name="华为云账户的ak")
    sk = models.CharField(max_length=255, verbose_name="华为云账户的sk")

    class Meta:
        db_table = "hw_cloud_account"
        verbose_name = "华为云账户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.account

    @classmethod
    def count_account(cls):
        return cls.objects.aggregate(count=Count('account'))

    @classmethod
    def all(cls):
        return cls.objects.all()

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()


class HWCloudProjectInfo(BaseModel):
    id = models.CharField(max_length=64, primary_key=True, verbose_name="华为云项目id")
    zone = models.CharField(max_length=32, verbose_name="华为云项目zone")
    account = models.ForeignKey(HWCloudAccount, on_delete=models.CASCADE, verbose_name="外键，关联华为云的账户id")

    class Meta:
        db_table = "hw_cloud_project_info"
        verbose_name = "华为云项目信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)

    @classmethod
    def get(cls, value):
        return cls.objects.filter(account__id=value)

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()


class ServiceInfo(BaseModel):
    service_name = models.CharField(max_length=64, null=True, verbose_name="服务名称")
    namespace = models.CharField(max_length=64, null=True, verbose_name="命名空间")
    cluster = models.CharField(max_length=64, null=True, verbose_name="集群名称")
    region = models.CharField(max_length=64, null=True, verbose_name="区域")

    class Meta:
        db_table = "service_info"
        verbose_name = "服务信息表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)

    @classmethod
    def count_id(cls):
        return cls.objects.aggregate(count=Count('id'))

    @classmethod
    def count_namespace(cls, namespace):
        return cls.objects.filter(namespace=namespace).count()

    @classmethod
    def get_service_info(cls, service_name, namespace, cluster, region):
        return cls.objects.filter(service_name=service_name, namespace=namespace, cluster=cluster, region=region)

    @classmethod
    def filter(cls, filter_name, filter_value):
        if filter_name and filter_name == "service_name":
            if filter_value:
                service_info_list = cls.objects.filter(service_name__contains=filter_value)
            else:
                service_info_list = cls.objects.filter(service_name=filter_value)
        elif filter_name and filter_name == "namespace":
            if filter_value:
                service_info_list = cls.objects.filter(namespace__contains=filter_value)
            else:
                service_info_list = cls.objects.filter(namespace=filter_value)
        elif filter_name and filter_name == "base_image":
            if filter_value:
                service_info_list = ServiceImage.objects.filter(base_image__contains=filter_value)
            else:
                service_info_list = ServiceImage.objects.filter(base_image=None)
            service_id = [service_info.service.id for service_info in service_info_list]
            service_info_list = cls.objects.filter(id__in=service_id)
        elif filter_name and filter_name == "base_os":
            if filter_value:
                service_info_list = ServiceImage.objects.filter(base_os__contains=filter_value)
            else:
                service_info_list = ServiceImage.objects.filter(base_os=None)
            service_id = [service_info.service.id for service_info in service_info_list]
            service_info_list = cls.objects.filter(id__in=service_id)
        elif filter_name and filter_name == "repository":
            if filter_value:
                service_info_list = ServiceImage.objects.filter(repository__contains=filter_value)
            else:
                service_info_list = ServiceImage.objects.filter(repository=None)
            service_id = [service_info.service.id for service_info in service_info_list]
            service_info_list = cls.objects.filter(id__in=service_id)
        else:
            service_info_list = cls.objects.all()
        return service_info_list

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()


class ServiceImage(BaseModel):
    image = models.CharField(max_length=128, null=True, verbose_name="镜像路径")
    repository = models.CharField(max_length=128, null=True, verbose_name="仓库")
    branch = models.CharField(max_length=64, null=True, verbose_name="分支")
    developer = models.CharField(max_length=64, null=True, verbose_name="开发者")
    email = models.EmailField(null=True)
    base_image = models.CharField(max_length=128, null=True, verbose_name="基础构建镜像")
    base_os = models.CharField(max_length=128, null=True, verbose_name="基础操作系统")
    pipline_url = models.CharField(max_length=256, null=True, verbose_name="流水线url")
    num_download = models.IntegerField(null=True, verbose_name="下载次数")
    size = models.CharField(max_length=32, null=True, verbose_name="镜像大小")
    cpu_limit = models.CharField(max_length=64, null=True, verbose_name="cpu限制")
    mem_limit = models.CharField(max_length=64, null=True, verbose_name="内存限制")
    service = models.ForeignKey(ServiceInfo, default="", on_delete=models.SET_DEFAULT)

    class Meta:
        db_table = "service_image"
        verbose_name = "服务镜像表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)

    @classmethod
    def get_all_image(cls):
        return cls.objects.values("image").distinct()

    @classmethod
    def update_images(cls, image,  **kwargs):
        return cls.objects.filter(image=image).update(**kwargs)

    @classmethod
    def get_by_image(cls, image, service_id):
        return cls.objects.filter(image=image, service__id=service_id).count()

    @classmethod
    def get(cls, service_id, fileds):
        return cls.objects.filter(service_id=service_id).values(fileds)

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()

    @classmethod
    def get_image(cls):
        return cls.objects.all().values("repository", "branch", "developer", "email").distinct()


class ServiceSla(BaseModel):
    # sla is unique to url
    url = models.CharField(max_length=64, null=True, verbose_name="服务域名")
    service_alias = models.CharField(max_length=64, null=True, verbose_name="服务别名")
    service_introduce = models.CharField(max_length=64, null=True, verbose_name="服务介绍")
    service_zone = models.CharField(max_length=64, null=True, verbose_name="服务归属社区")
    month_abnormal_time = models.FloatField(null=True, verbose_name="月度异常累计时间")
    year_abnormal_time = models.FloatField(null=True, verbose_name="年度异常累计时间")
    month_sla = models.FloatField(null=True, verbose_name="月度sla")
    year_sla = models.FloatField(null=True, verbose_name="年度sla")
    remain_time = models.FloatField(null=True, verbose_name="年度剩余sla配额")
    service = models.ForeignKey(ServiceInfo, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "service_sla"
        verbose_name = "服务SLA表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)

    @classmethod
    def all(cls):
        return cls.objects.all().order_by("remain_time").values(
            "service_alias", "service_introduce", "url",
            "service_zone", "month_abnormal_time", "year_abnormal_time",
            "month_sla", "year_sla", "remain_time")

    @classmethod
    def get_by_url(cls, url):
        return cls.objects.filter(url=url).count()

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()

    @classmethod
    def update_url(cls, url, **kwargs):
        return cls.objects.filter(url=url).update(**kwargs)


# noinspection PyUnresolvedReferences
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
    refresh_time = models.DateTimeField(verbose_name="刷新时间")
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
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)

    @classmethod
    def filter(cls, filter_name, filter_value):
        if filter_name and filter_name == "eip":
            eip_list = cls.objects.filter(eip__contains=filter_value)
        elif filter_name and filter_name == "example_id":
            eip_list = cls.objects.filter(example_id__contains=filter_value)
        elif filter_name and filter_name == "example_name":
            eip_list = cls.objects.filter(example_name__contains=filter_value)
        elif filter_name and filter_name == "account":
            eip_list = cls.objects.filter(account__contains=filter_value)
        elif filter_name and filter_name == "eip_type":
            filter_value = HWCloudEipStatus.get_comment_status().get(filter_value, -1)
            eip_list = cls.objects.filter(eip_status__contains=filter_value)
        elif filter_name and filter_name == "eip_zone":
            eip_list = cls.objects.filter(eip_zone__contains=filter_value)
        else:
            eip_list = HWCloudEipInfo.objects.all()
        return eip_list

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()

    @classmethod
    def count_id(cls):
        return cls.objects.aggregate(count=Count('id'))
