from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

from django.views.generic import View


class ScanPortView(View):
    def get(self, request):

        return JsonResponse({"code": "200"})
