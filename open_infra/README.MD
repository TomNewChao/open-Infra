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

2.设置环境变量，可以保存到env.file中，启动时携带配置启动。
"pwd"=""
"mysql_host"="192.168.1.82"
"mysql_port"="3306"
"mysql_user"=""
"mysql_password"=""
"obs_ak"=""
"obs_sk"=""
"obs_url"="obs.cn-north-4.myhuaweicloud.com"
"obs_domain_id"=""
"uptime_robot_api_key"=""
"alarm_email_user"="osinfra"
"alarm_email_pwd"=""
"ALARM_SMS_URL"="https://smsapi.cn-south-1.myhuaweicloud.com:443/sms/batchSendSms/v1"
"ALARM_SMS_KEY"=""
"ALARM_SMS_SECRET"=""
"ALARM_SMS_SENDER"=""
"ALARM_SMS_ALARM_TEMPLATE"=""
"ALARM_SMS_RECOVER_TEMPLATE"=""
"GITHUB_SECRET"=""
~~~

3.启动容器

~~~bash
docker run -dit --env-file env.file --name open-infra-demo open-infra:latest
~~~

