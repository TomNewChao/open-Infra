# Register your models here.
from django.contrib import admin
from app_resources.models import ServiceInfo, ServiceImage, ServiceSla, ServiceIntroduce
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


class ServiceIntroduceAdmin(BaseAdmin):
    list_display = ["service_name", "service_introduce", "service_lang", "service_url", "service_zone"]
    search_fields = ["service_name", "service_introduce", "service_sla__url", "service_sla__service_zone"]

    def service_url(self, obj):
        if obj.service_sla is not None:
            return obj.service_sla.url

    def service_zone(self, obj):
        if obj.service_sla is not None:
            return obj.service_sla.service_zone


admin.site.register(ServiceInfo, ServiceInfoAdmin)
admin.site.register(ServiceSla, ServiceSlaAdmin)
admin.site.register(ServiceImage, ServiceImageAdmin)
admin.site.register(ServiceIntroduce, ServiceIntroduceAdmin)
