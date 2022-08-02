# frontend

## 背景

frontend是open-infra的前端项目，由vue架构编写，参考开源项目[vuestic-admin](https://github.com/TomNewChao/vuestic-admin) 站点进行二次开发

## 运行

1.本地执行安装

~~~bash
npm intall : 安装依赖包。

npm run dev: 运行。

npm run build 打包构建。
~~~

2.以dockerfile运行安装

~~~bash
1.需要修改nginx.conf里面的后端服务的端口配置：
proxy_pass http://172.17.0.9:80;

2.制作镜像
cd frontend
docker build -t open-infra-frontend:latest .
cker run -dit -p 8080:8080 --name front open-infra-frontend:latest
~~~



