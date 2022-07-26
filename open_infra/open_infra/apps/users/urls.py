from django.conf.urls import url
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token, obtain_jwt_token
from users.views import UserView, MessageView, LogInfoView

urlpatterns = [
    url(r'^user_info', UserView.as_view()),
    url(r'^message_count', MessageView.as_view()),
    url(r'^log_info', LogInfoView.as_view()),
    url(r'^login', obtain_jwt_token),
    url(r'^refresh_token', refresh_jwt_token),
    url(r'^verify_token', verify_jwt_token),
]
