# -*- coding: utf-8 -*-
# @Time    : 2022/6/8 17:30
# @Author  : Tom_zc
# @FileName: models.py
# @Software: PyCharm
from itertools import chain
from django.db import models


class BaseModel(models.Model):
    """
    模型基类，封装公共属性及方法
    """

    class Meta:
        abstract = True

    def __getitem__(self, item):
        """实现模型对象可以通过字典的方式获取值"""
        return getattr(self, item)

    @classmethod
    def get_model_field(cls):
        """获取模型的所有字段名列表
        :return:
        :rtype: list
        """
        fields_obj = cls._meta.fields
        return [i.name for i in fields_obj]

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
            dict_data[f.name] = value
        return dict_data

    objects = models.Manager()


class ExtraBaseModel(models.Model):
    """为模型类补充字段"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表
        abstract = True
