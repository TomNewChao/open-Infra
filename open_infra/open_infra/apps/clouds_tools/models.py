from itertools import chain

from clouds_tools.resources.constants import HWCloudEipStatus, HWCloudEipType
from open_infra.utils.models import BaseModel
from django.db import models
from django.conf import settings


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

    def __str__(self):
        return str(self.id)


class HWCloudScanEipPortStatus(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    status = models.IntegerField(verbose_name="操作状态")

    class Meta:
        db_table = "hw_cloud_scan_eip_port_status"
        verbose_name = "华为云高危端口扫描状态表"

    def __str__(self):
        return str(self.account)


class HWCloudScanEipPortInfo(BaseModel):
    eip = models.GenericIPAddressField(verbose_name="华为云EIP")
    port = models.IntegerField(verbose_name="华为云EIP的暴露端口")
    status = models.CharField(max_length=64, null=True, verbose_name="端口状态")
    link_protocol = models.CharField(max_length=64, null=True, verbose_name="端口链接协议")
    transport_protocol = models.CharField(max_length=64, null=True, verbose_name="端口传输协议")
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    region = models.CharField(max_length=32, verbose_name="华为云项目区域")
    service_info = models.CharField(max_length=128, null=True, verbose_name="服务器版本信息")
    protocol = models.IntegerField(verbose_name="协议:1_tcp/0_udp")

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

    def __str__(self):
        return str(self.eip)


class HWCloudScanObsAnonymousStatus(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    status = models.IntegerField(verbose_name="操作状态")

    class Meta:
        db_table = "hw_cloud_scan_obs_anonymous_bucket_status"
        verbose_name = "华为云对象系统匿名桶状态表"

    def __str__(self):
        return str(self.account)


class HWCloudScanObsAnonymousBucket(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    bucket = models.CharField(max_length=128, verbose_name="华为云对象系统匿名桶")
    url = models.CharField(max_length=256, null=True, verbose_name="华为云对象系统匿名桶的url")

    class Meta:
        db_table = "hw_cloud_scan_obs_anonymous_bucket"
        verbose_name = "华为云对象系统匿名桶"

    def __str__(self):
        return str(self.bucket)


class HWCloudScanObsAnonymousFile(BaseModel):
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    bucket = models.CharField(max_length=128, verbose_name="华为云对象系统匿名桶")
    url = models.CharField(max_length=256, null=True, verbose_name="华为云对象系统匿名文件的url")
    path = models.CharField(max_length=256, null=True, verbose_name="华为云对象系统匿名文件的path")
    data = models.CharField(max_length=256, null=True, verbose_name="华为云对象系统匿名文件的敏感数据")

    class Meta:
        db_table = "hw_cloud_scan_obs_anonymous_file"
        verbose_name = "华为云对象系统匿名文件"

    def __str__(self):
        return str(self.bucket)


class HWCloudHighRiskPort(BaseModel):
    port = models.IntegerField(verbose_name="高危端口")
    desc = models.CharField(max_length=255, verbose_name="高危端口")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "hw_cloud_high_risk_port"
        verbose_name = "华为云高危端口"

    def __str__(self):
        return str(self.port)


class HWColudObsInteract(BaseModel):
    username = models.CharField(max_length=64, verbose_name="华为云IAM用户")
    community = models.CharField(max_length=16, verbose_name="社区")
    user_id = models.CharField(max_length=32, verbose_name="用户id")
    password = models.CharField(max_length=64, verbose_name="用户密码")
    is_delete = models.BooleanField(default=False, verbose_name="软删除")

    class Meta:
        db_table = "hw_cloud_obs_interact"
        verbose_name = "华为云对象上传系统"

    def __str__(self):
        return str(self.id)


class ServiceInfo(BaseModel):
    service_name = models.CharField(max_length=64, null=True, verbose_name="服务名称:argocd")
    service_alias = models.CharField(max_length=64, null=True, verbose_name="服务别名")
    url = models.URLField(null=True, verbose_name="域名： argocd")
    url_alias = models.URLField(null=True, verbose_name="域名别名")
    namespace = models.CharField(max_length=64, null=True, verbose_name="命名空间")
    cluster = models.CharField(max_length=64, null=True, verbose_name="集群名")
    service_introduce = models.CharField(max_length=64, null=True, verbose_name="服务介绍")
    community = models.CharField(max_length=16, null=True, verbose_name="社区")
    month_abnormal_time = models.FloatField(null=True, verbose_name="月度异常累计时间")
    year_abnormal_time = models.FloatField(null=True, verbose_name="年度异常累计时间")
    month_sla = models.FloatField(null=True, verbose_name="月度sla")
    year_sla = models.FloatField(null=True, verbose_name="年度sla")
    remain_time = models.FloatField(null=True, verbose_name="年度剩余sla配额")

    class Meta:
        db_table = "service_info"
        verbose_name = "service_info信息表"

    def __str__(self):
        return self.id
