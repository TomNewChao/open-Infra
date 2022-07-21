#!/usr/bin/env bash

yum install nmap
pip3 install huaweicloudsdkeip
pip3 install huaweicloudsdknat
pip3 install huaweicloudsdkelb
pip3 install huaweicloudsdkbms
pip3 install huaweicloudsdkecs
pip3 install huaweicloudsdkrds
pip3 install huaweicloudsdkvpc
pip3 install openpyxl
pip3 install PyYAML

pip3 install django
pip3 install django_redis
pip3 install djangorestframework-jwt
pip3 install django-cors-header


python3 manager.py makemigrations