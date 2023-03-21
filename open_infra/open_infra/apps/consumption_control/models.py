# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Sum

from open_infra.utils.models import BaseModel


class HWCloudBillInfo(BaseModel):
    bill_cycle = models.CharField(max_length=16, verbose_name="账期(单位月)")
    account = models.CharField(max_length=32, verbose_name="华为云账户名称")
    resource_type_name = models.CharField(max_length=64, verbose_name="云服务类型名称")
    consume_amount = models.FloatField(verbose_name="应付金额")
    discount_rate = models.FloatField(null=True, verbose_name="折扣率")
    actual_cost = models.FloatField(null=True, verbose_name="实际费用")

    class Meta:
        db_table = "hw_cloud_bill_info"
        verbose_name = "华为云账单信息"
        verbose_name_plural = verbose_name

    @classmethod
    def filter(cls, filter_name, filter_value):
        if filter_name and filter_name == "account":
            bill_info_list = cls.objects.filter(account__contains=filter_value)
        elif filter_name and filter_name == "bill_cycle":
            bill_info_list = cls.objects.filter(bill_cycle__contains=filter_value)
        elif filter_name and filter_name == "resource_type_name":
            bill_info_list = cls.objects.filter(resource_type_name__contains=filter_value)
        else:
            bill_info_list = cls.objects.all()
        return bill_info_list

    @classmethod
    def count_acount(cls):
        return cls.objects.order_by("account").values("account").distinct()

    @classmethod
    def count_resource_type_name(cls):
        return cls.objects.order_by("resource_type_name").values("resource_type_name").distinct()

    @classmethod
    def bill_list(cls, account_name, sorted_month_list):
        return cls.objects.filter(account=account_name).filter(bill_cycle__in=sorted_month_list).values(
            "bill_cycle").annotate(consume=Sum("actual_cost")).values("consume", "bill_cycle").order_by("bill_cycle")

    @classmethod
    def count_bill_cycle(cls):
        return cls.objects.order_by("-bill_cycle").values("bill_cycle").distinct()

    @classmethod
    def count_consume_type(cls, account, bill_cycle):
        return cls.objects.filter(account=account, bill_cycle=bill_cycle).values("resource_type_name"). \
                   annotate(consume=Sum("actual_cost")).values("consume", "resource_type_name").order_by("-consume")[:5]

    @classmethod
    def count_actual_cost(cls, account, bill_cycle):
        return cls.objects.filter(account=account, bill_cycle=bill_cycle).aggregate(Sum("actual_cost"))

    @classmethod
    def query_bill_by_account(cls, account):
        return cls.objects.filter(account=account).distinct().order_by("bill_cycle").values("bill_cycle")


class CpuResourceUtilization(BaseModel):
    name = models.CharField(max_length=256, null=True, verbose_name="服务器名称")
    create_time = models.IntegerField(null=True, verbose_name="创建时间戳")
    lower_cpu_count = models.IntegerField(null=True, verbose_name="低cpu统计:<10%的cpu统计个数, 不包含10%")
    medium_lower_cpu_count = models.IntegerField(null=True, verbose_name="中低cpu统计:10-50%的cpu统计个数, 不包含50%")
    medium_high_cpu_count = models.IntegerField(null=True, verbose_name="中高cpu统计:50-90%的cpu统计个数, 不包含90%")
    high_cpu_count = models.IntegerField(null=True, verbose_name="高cpu统计:>90%的cpu统计个数")

    class Meta:
        db_table = "cpu_resource_utilization"
        verbose_name = "服务器cpu资源利用率统计"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id

    @classmethod
    def delete_con(cls, expire_timestamps):
        return cls.objects.filter(create_time__lt=expire_timestamps).delete()

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)


class MemResourceUtilization(BaseModel):
    name = models.CharField(max_length=256, null=True, verbose_name="服务器名称")
    create_time = models.IntegerField(null=True, verbose_name="创建时间戳")
    lower_mem_count = models.IntegerField(null=True, verbose_name="低mem统计:<10%的cpu统计个数, 不包含10%")
    medium_lower_mem_count = models.IntegerField(null=True, verbose_name="中低mem统计:10-50%的cpu统计个数, 不包含50%")
    medium_high_mem_count = models.IntegerField(null=True, verbose_name="中高mem统计:50-90%的cpu统计个数, 不包含90%")
    high_mem_count = models.IntegerField(null=True, verbose_name="高mem统计:>90%的mem统计个数")

    class Meta:
        db_table = "mem_resource_utilization"
        verbose_name = "服务器内存资源利用率统计"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id

    @classmethod
    def delete_con(cls, expire_timestamps):
        return cls.objects.filter(create_time__lt=expire_timestamps).delete()

    @classmethod
    def create_single(cls, **kwargs):
        return cls.objects.create(**kwargs)
