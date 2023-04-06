# Register your models here.
from django.contrib import admin
from app_resources.models import ServiceInfo, ServiceImage, ServiceSla
from open_infra.utils.admin import BaseAdmin


class ServiceInfoAdmin(BaseAdmin):
    list_display = ["service_name", "namespace", "cluster", "region"]
    search_fields = ["service_name", "namespace", "cluster", "region"]


class ServiceSlaAdmin(BaseAdmin):
    list_display = [field.name for field in ServiceSla._meta.get_fields()]
    search_fields = ["url", "service_alias", "service_zone", "service__service_name"]


class ServiceImageAdmin(BaseAdmin):
    list_display = [field.name for field in ServiceImage._meta.get_fields()]
    search_fields = ["image", "developer", "email", "service__service_name"]


admin.site.register(ServiceInfo, ServiceInfoAdmin)
admin.site.register(ServiceSla, ServiceSlaAdmin)
admin.site.register(ServiceImage, ServiceImageAdmin)
