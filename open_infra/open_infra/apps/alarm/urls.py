from django.conf.urls import url
from alarm.views import AlarmView, AlarmNotifyView, BatchAlarmNotifyView, AlarmNameView

urlpatterns = [
    url(r'^alarm$', AlarmView.as_view()),
    url(r'^alarm_name$', AlarmNameView.as_view()),
    url(r'^alarm_notify$', AlarmNotifyView.as_view()),
    url(r'^batch_alarm_notify$', BatchAlarmNotifyView.as_view()),
]
