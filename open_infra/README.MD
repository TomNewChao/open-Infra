# open-infra

# 背景

将端口扫描工具和对象扫描工具服务化，特意开发open-infra项目，该项目由前端vue+后端django搭建。

# 安装

1.生成镜像

~~~bash
cd open_infra
docker build -t open-infra:latest .
~~~

2.环境预制

~~~bash
1.搭建一个mysql数据库，创建数据库：open_infra
~~~

3.启动容器

~~~bash
docker run -dit 
--env secret="" # django的secret
--env mysql_host=""  # mysql的ip
--env mysql_port="" # mysql的端口 
--env mysql_user="" # mysql的用户
--env mysql_password="" # mysql数据库的密码
--env obs_ak="" #华为云obs的ak
--env obs_sk="" #华为云obs的sk
--env obs_url="" #华为云obs的url
--name open-infra-demo open-infra:latest
~~~

