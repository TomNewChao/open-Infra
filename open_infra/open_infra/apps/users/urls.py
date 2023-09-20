from django.conf.urls import url
from users.views import UserView, MessageView, LogInfoView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    url(r'^user_info', UserView.as_view()),
    url(r'^message_count', MessageView.as_view()),
    url(r'^log_info', LogInfoView.as_view()),
    url(r'^login', TokenObtainPairView.as_view()),
    url(r'^refresh_token', TokenRefreshView.as_view()),
]
