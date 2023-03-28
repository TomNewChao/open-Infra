from open_infra.utils.auth_permisson import AuthView
# from rest_framework_jwt.utils import jwt_decode_handler
# from users.models import User


class UserView(AuthView):

    def get(self, request):
        # token = request.headers.get("Authorization")
        # token_list = token.split("Bearer ")
        # toke_dict = jwt_decode_handler(token_list[1])
        # user_obj = User.objects.get(username=toke_dict["username"])
        data = {
            "avatar": "admin",
            "name": "admin",
            "user_id": 1,
            "access": ["admin", "admin"],

        }
        return data


class MessageView(AuthView):
    def get(self, request):
        data = {
            "msg_count": 0,
        }
        return data


class LogInfoView(AuthView):
    def post(self, request):
        return dict()
