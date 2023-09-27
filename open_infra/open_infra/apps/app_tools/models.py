from itertools import chain
from open_infra.utils.models import BaseModel
from django.db import models
from django.conf import settings


class HWCloudScanEipPortStatus(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    status = models.IntegerField(verbose_name="操作状态")

    class Meta:
        db_table = "hw_cloud_scan_eip_port_status"
        verbose_name = "华为云高危端口扫描状态表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.account)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()

    @classmethod
    def save_scan_eip_port_status(cls, account, status):
        return cls.objects.create(account=account, status=status)

    @classmethod
    def query_scan_eip_port_status(cls, account):
        try:
            return cls.objects.get(account=account)
        except cls.DoesNotExist:
            return None

    @classmethod
    def create_all(cls, status_list):
        return cls.objects.bulk_create(status_list)

    @classmethod
    def update_status(cls, account_list, status):
        return HWCloudScanEipPortStatus.objects.filter(account__in=account_list).update(status=status)


class HWCloudScanEipPortInfo(BaseModel):
    eip = models.GenericIPAddressField(verbose_name="华为云EIP")
    port = models.IntegerField(verbose_name="华为云EIP的暴露端口")
    status = models.CharField(max_length=64, null=True, verbose_name="端口状态")
    link_protocol = models.CharField(max_length=64, null=True, verbose_name="端口链接协议")
    transport_protocol = models.CharField(max_length=64, null=True, verbose_name="端口传输协议")
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    region = models.CharField(max_length=32, verbose_name="华为云项目区域")
    service_info = models.CharField(max_length=2048, null=True, verbose_name="服务器版本信息")
    protocol = models.IntegerField(verbose_name="协议:1_tcp/0_udp")

    # noinspection PyUnresolvedReferences
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
            if f.name == "region":
                value = settings.ZONE_ALIAS_DICT.get(value)
            dict_data[f.name] = value
        return dict_data

    class Meta:
        db_table = "hw_cloud_scan_eip_port_info"
        verbose_name = "华为云高危端口扫描信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.eip)

    @classmethod
    def equal_account(cls, account):
        return cls.objects.filter(account=account)

    @classmethod
    def filter_account(cls, account_list):
        return cls.objects.filter(account__in=account_list)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)


class HWCloudScanObsAnonymousStatus(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    status = models.IntegerField(verbose_name="操作状态")

    class Meta:
        db_table = "hw_cloud_scan_obs_anonymous_bucket_status"
        verbose_name = "华为云对象系统匿名桶状态表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.account)

    @classmethod
    def query_scan_obs_status(cls, account):
        try:
            return cls.objects.get(account=account)
        except cls.DoesNotExist:
            return None

    @classmethod
    def save_scan_obs_status(cls, account, status):
        return cls.objects.create(account=account, status=status)

    @classmethod
    def create_all(cls, status_list):
        return cls.objects.bulk_create(status_list)

    @classmethod
    def get(cls, account_list, status):
        return cls.objects.filter(account__in=account_list).update(status=status)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()


class HWCloudScanObsAnonymousBucket(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    bucket = models.CharField(max_length=128, verbose_name="华为云对象系统匿名桶")
    url = models.CharField(max_length=256, null=True, verbose_name="华为云对象系统匿名桶的url")

    class Meta:
        db_table = "hw_cloud_scan_obs_anonymous_bucket"
        verbose_name = "华为云对象系统匿名桶"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.bucket)

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def equal_account(cls, account):
        return cls.objects.filter(account=account)

    @classmethod
    def filter_account(cls, account_list):
        return cls.objects.filter(account__in=account_list)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()


class HWCloudScanObsAnonymousFile(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    bucket = models.CharField(max_length=128, verbose_name="华为云对象系统匿名桶")
    url = models.CharField(max_length=256, null=True, verbose_name="华为云对象系统匿名文件的url")
    path = models.CharField(max_length=256, null=True, verbose_name="华为云对象系统匿名文件的path")
    data = models.CharField(max_length=256, null=True, verbose_name="华为云对象系统匿名文件的敏感数据")

    class Meta:
        db_table = "hw_cloud_scan_obs_anonymous_file"
        verbose_name = "华为云对象系统匿名文件"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.bucket)

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def equal_account(cls, account):
        return cls.objects.filter(account=account)

    @classmethod
    def filter_account(cls, account_list):
        return cls.objects.filter(account__in=account_list)

    @classmethod
    def delete_all(cls):
        return cls.objects.all().delete()


class HWCloudHighRiskPort(BaseModel):
    port = models.IntegerField(verbose_name="高危端口")
    desc = models.CharField(max_length=255, verbose_name="高危端口")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "hw_cloud_high_risk_port"
        verbose_name = "华为云高危端口"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.port)

    @classmethod
    def all(cls):
        return cls.objects.all()

    @classmethod
    def filter(cls, filter_value):
        return cls.objects.filter(port__contains=filter_value)

    @classmethod
    def create_all(cls, save_list_data):
        return cls.objects.bulk_create(save_list_data)

    @classmethod
    def query_high_risk_port(cls, port):
        try:
            return cls.objects.get(port=port)
        except cls.DoesNotExist:
            return None

    @classmethod
    def create_single(cls, port, desc):
        return cls.objects.create(port=port, desc=desc)

    @classmethod
    def delete_single(cls, port_list):
        return cls.objects.filter(port__in=port_list).delete()
