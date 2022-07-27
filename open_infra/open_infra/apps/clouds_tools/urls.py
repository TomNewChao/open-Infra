from django.conf.urls import url
from clouds_tools.views import ScanPortProgressView, ScanPortView, ScanObsView, ScanObsProgressView, SingleScanPortView, SingleScanObsView

urlpatterns = [
    url(r'^scan_port/progress$', ScanPortProgressView.as_view()),
    url(r'^scan_port$', ScanPortView.as_view()),
    url(r'^scan_obs/progress$', ScanObsProgressView.as_view()),
    url(r'^scan_obs$', ScanObsView.as_view()),

    url(r'^single_scan_port$', SingleScanPortView.as_view()),
    url(r'^single_scan_obs$', SingleScanObsView.as_view()),
]
