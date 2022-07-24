import json
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.generic import View
from rest_framework_jwt.utils import jwt_decode_handler

from open_infra.utils.api_error_code import ErrCode
from open_infra.utils.common import assemble_api_result
from users.models import User


class UserView(View):

    def get(self, request):
        token = request.GET.get("token")
        toke_dict = jwt_decode_handler(token)
        user_obj = User.objects.get(username=toke_dict["username"])
        data = {
            "avatar": user_obj.username,
            "name": user_obj.username,
            "user_id": user_obj.id,
            "access": [user_obj.username, "admin"],

        }
        return JsonResponse(data)


class MessageView(View):
    def get(self, request):
        data = {
            "msg_count": 0,
        }
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)


class LogInfoView(View):
    def post(self, request):
        data = {

        }
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=data)
