from rest_framework.routers import DefaultRouter
from alarm.views import AlarmView, AlarmNotifyView


urlpatterns = list()
router = DefaultRouter()
router.register("alarm", AlarmView, basename="alarm")
router.register("alarm_notify", AlarmNotifyView, basename="alarm_notify")
urlpatterns += router.urls
