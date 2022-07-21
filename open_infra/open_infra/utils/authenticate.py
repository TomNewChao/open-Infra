from django.contrib.auth.backends import ModelBackend
from users.models import User
import re


class UserModelBackend(ModelBackend):
    # 鉴定客户是以手机号登录还是以账户名登录
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 如果request为None说明是admin登录
        if request is None:
            try:
                user = User.objects.get(username=username)
            except Exception as e:
                return None
            # 鉴定密码
            if not user.check_password(password):
                return None
            # 鉴定是不是管理员权限
            if user.is_staff or user.is_superuser:
                return user
            else:
                return None

        # 如果admin不为None，说明是普通用户登录
        else:
            try:
                user = User.objects.get(username=username)
            except Exception as e:
                try:
                    user = User.objects.get(mobile=username)
                except Exception as e:
                    return None
            # 鉴定密码
            if user.check_password(password):
                return user
            else:
                return None


