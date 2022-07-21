from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^scan_port/progress$', views.ScanPortProgressView.as_view()),
    url(r'^scan_port/$', views.ScanPortView.as_view()),
]
