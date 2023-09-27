from django.conf.urls import url
from users.views import LoginView, RefreshTokenView, LogoutView, UserView, MessageView
from rest_framework.routers import DefaultRouter

urlpatterns = [
    url(r'^login/', LoginView.as_view()),
    url(r'^refresh_token/', RefreshTokenView.as_view()),
]

router = DefaultRouter()
router.register("logout", LogoutView, basename="logout")
router.register("user_info", UserView, basename="user_info")
router.register("message_count", MessageView, basename="message_count")

urlpatterns += router.urls
