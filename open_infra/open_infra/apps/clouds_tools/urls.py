from django.conf.urls import url
from clouds_tools.views import ScanPortProgressView, ScanPortView, ScanObsView, ScanObsProgressView

urlpatterns = [
    url(r'^scan_port/progress$', ScanPortProgressView.as_view()),
    url(r'^scan_port$', ScanPortView.as_view()),
    url(r'^scan_obs/progress$', ScanObsProgressView.as_view()),
    url(r'^scan_obs$', ScanObsView.as_view()),
]
