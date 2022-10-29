from django.conf.urls import url
from clouds_tools.views import ScanPortView, ScanObsView, SingleScanPortView, SingleScanObsView, PortsListView, EipView, \
    PortsListDeleteView, ServiceView, SlaExportView, ObsInteractView

urlpatterns = [
    # query/create/delete high level port
    url(r'^high_risk_port$', PortsListView.as_view()),
    url(r'^bulk_high_risk_port$', PortsListDeleteView.as_view()),
    url(r'^scan_port$', ScanPortView.as_view()),
    url(r'^single_scan_port$', SingleScanPortView.as_view()),
    url(r'^single_scan_port/progress$', SingleScanPortView.as_view()),

    # scan obs anonymous bucket
    url(r'^scan_obs$', ScanObsView.as_view()),
    url(r'^single_scan_obs$', SingleScanObsView.as_view()),
    url(r'^single_scan_obs/progress$', SingleScanObsView.as_view()),

    #  query eip
    url(r'^eip$', EipView.as_view()),

    #  query cla
    url(r'^service$', ServiceView.as_view()),
    url(r'^sla_export$', SlaExportView.as_view()),

    # obs_interact is solve for using github to get config to upload file to obs
    # Detail: https://github.com/Open-Infra-Ops/obs-interact
    url(r'obs_interact', ObsInteractView.as_view())

]
