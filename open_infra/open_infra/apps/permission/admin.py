from django.contrib import admin

# Register your models here.
from permission.models import KubeConfigInfo
from open_infra.utils.admin import BaseAdmin


class KubeConfigInfoAdmin(BaseAdmin):
    list_display = [field.name for field in KubeConfigInfo._meta.get_fields()]


admin.site.register(KubeConfigInfo, KubeConfigInfoAdmin)
