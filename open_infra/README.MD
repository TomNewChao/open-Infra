# open-infra

# 背景

open-infra项目是openEuler的运维管理平台。

# 安装

1.生成镜像

~~~bash
cd open_infra
docker build -t open-infra:latest .
~~~

2.环境预制

~~~bash
1.搭建一个mysql数据库，创建数据库：open_infra

2.填写配置文件: open_infra/config/secret
pwd: 
mysql_host: 
mysql_port: 
mysql_user: 
mysql_password: 
obs_ak: 
obs_sk: 
obs_url: 
obs_domain_id: 
uptime_robot_api_key:
alarm_email_host: 
alarm_email_user: 
alarm_email_pwd: 
ALARM_SMS_URL: 
ALARM_SMS_KEY: 
ALARM_SMS_SECRET: 
ALARM_SMS_SENDER: 
ALARM_SMS_ALARM_TEMPLATE: 
ALARM_SMS_RECOVER_TEMPLATE: 
GITHUB_SECRET: 
~~~

3.启动容器

~~~bash
docker run -dit --env-file env.file --name open-infra-demo open-infra:latest
~~~

4.启动定时任务

~~~bash
python3 manage.py refresh_resource_command                 # every day 0:00
python3 manage.py scan_port_command                        # every day 1:00
python3 manage.py refresh_bill_command                     # month day0 2:00
python3 manage.py refresh_refresh_resource_command         # every week 3:00
python3 manage.py clean_expired_command         		   # every 10 minutes
~~~