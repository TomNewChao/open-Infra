import traceback
from logging import getLogger
from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django_redis import get_redis_connection
from django.conf import settings

from open_infra.utils.api_error_code import ErrCode
from open_infra.utils.common import assemble_api_result
from users.models import User

logger = getLogger("django")


class LoginView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        session = get_redis_connection("session")
        username = request.data["username"]
        token_exp = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
        blacklist_exp = settings.LOGIN_FAILED_BLACKLIST_LIFETIME
        blacklist_count = settings.LOGIN_FAILED_BLACKLIST_COUNT
        try:
            result = super().post(request, *args, **kwargs)
            session.set(username, "0", token_exp)
            return assemble_api_result(ErrCode.STATUS_SUCCESS, data=result.data)
        except exceptions.AuthenticationFailed:
            if session.get(username):
                failed_count = int(session.get(username))
            else:
                failed_count = 0
            failed_count += 1
            logger.error("[LoginView] auth failed:{}, count:{}".format(username, str(failed_count)))
            if failed_count >= blacklist_count:
                return assemble_api_result(ErrCode.STATUS_USER_DISABLED_FAIL)
            session.set(username, str(failed_count), blacklist_exp)
            return assemble_api_result(ErrCode.STATUS_USER_LOGIN_FAIL)
        except Exception as e:
            logger.error("[LoginView] err:{}, traceback:{}".format(e, traceback.format_exc()))
            return assemble_api_result(ErrCode.INTERNAL_ERROR)


class RefreshTokenView(TokenRefreshView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        username = request.user.username
        session = get_redis_connection("session")
        token_exp = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
        result = super().post(request, *args, **kwargs)
        session.set(username, "0", token_exp)
        return assemble_api_result(ErrCode.STATUS_SUCCESS, data=result.data)


class LogoutView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def create(self, request, *args, **kwargs):
        username = request.user.username
        session = get_redis_connection("session")
        session.delete(username)
        return assemble_api_result(ErrCode.STATUS_SUCCESS)


class UserView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def list(self, request, *args, **kwargs):
        username = request.user.username
        user = User.get_user_info(username)
        data = {
            "avatar": settings.AVATAR_URL,
            "name": user.username,
            "user_id": user.id,
            "access": ["admin", "admin"],
        }
        if user.is_superuser:
            data["access"] = ["admin"]
        else:
            data["access"] = ["system"]
        return assemble_api_result(err_code=ErrCode.STATUS_SUCCESS, data=data)


class MessageView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def list(self, request):
        data = {
            "msg_count": 0,
        }
        return assemble_api_result(err_code=ErrCode.STATUS_SUCCESS, data=data)
