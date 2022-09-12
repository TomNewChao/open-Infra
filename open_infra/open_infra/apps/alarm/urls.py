from django.conf.urls import url
from alarm.views import AlarmView, AlarmEmailView, AlarmEmailListView

urlpatterns = [
    url(r'^alarm_email$', AlarmEmailView.as_view()),
    url(r'^alarm_email_list$', AlarmEmailListView.as_view()),
    url(r'^alarm$', AlarmView.as_view()),
]
