# -*- coding: utf-8 -*-
# @Time    : 2022/7/25 14:39
# @Author  : Tom_zc
# @FileName: auth_permisson.py
# @Software: PyCharm
import time
import jwt
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View
from rest_framework_jwt.utils import jwt_decode_handler
from open_infra.utils.common import auto_response
from users.models import User


class AuthView(View):
    """auth view"""

    @staticmethod
    def _auth_user(request):
        token = request.headers.get("Authorization")
        if token is None:
            return HttpResponseForbidden()
        token_list = token.split("Bearer ")
        try:
            toke_dict = jwt_decode_handler(token_list[1])
        except jwt.exceptions.ExpiredSignatureError:
            return HttpResponseForbidden()
        user_obj = User.objects.get(id=toke_dict["user_id"])
        if not user_obj:
            return HttpResponseForbidden()
        cur_timestamp = int(time.time())
        if cur_timestamp > int(toke_dict["exp"]):
            return HttpResponseForbidden()
        return True

    @auto_response()
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            auth_result = self._auth_user(request)
            if isinstance(auth_result, HttpResponse):
                return auth_result
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
