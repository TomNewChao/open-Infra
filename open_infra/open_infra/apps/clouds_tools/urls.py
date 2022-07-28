from django.conf.urls import url
from clouds_tools.views import ScanPortView, ScanObsView, SingleScanPortView, SingleScanObsView, \
    SingleScanPortProgressView, SingleScanObsProgressView

urlpatterns = [
    url(r'^scan_port$', ScanPortView.as_view()),
    url(r'^scan_obs$', ScanObsView.as_view()),

    url(r'^single_scan_port/progress$', SingleScanPortProgressView.as_view()),
    url(r'^single_scan_port$', SingleScanPortView.as_view()),
    url(r'^single_scan_obs/progress$', SingleScanObsProgressView.as_view()),
    url(r'^single_scan_obs$', SingleScanObsView.as_view()),
]
