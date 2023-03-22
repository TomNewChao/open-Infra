# Register your models here.
from django.contrib import admin
from app_resources.models import ServiceInfo, ServiceImage, ServiceSla
from open_infra.utils.admin import BaseAdmin


class ServiceInfoAdmin(BaseAdmin):
    list_display = ["service_name", "namespace", "cluster", "region"]


class ServiceSlaAdmin(BaseAdmin):
    list_display = [field.name for field in ServiceSla._meta.get_fields()]


class ServiceImageAdmin(BaseAdmin):
    list_display = [field.name for field in ServiceImage._meta.get_fields()]


admin.site.register(ServiceInfo, ServiceInfoAdmin)
admin.site.register(ServiceSla, ServiceSlaAdmin)
admin.site.register(ServiceImage, ServiceImageAdmin)
