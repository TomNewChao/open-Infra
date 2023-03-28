# Register your models here.
from django.contrib import admin
from users.models import User
from open_infra.utils.admin import BaseAdmin

admin.site.register(User, BaseAdmin)
