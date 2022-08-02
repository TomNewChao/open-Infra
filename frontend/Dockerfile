FROM centos:7 as builder

RUN mkdir /opt/node
RUN mkdir -p /home/open-infra/web
WORKDIR /home/open-infra/web

RUN yum update -y
RUN yum install wget -y
RUN cd /opt/node && wget https://npmmirror.com/mirrors/node/v16.16.0/node-v16.16.0-linux-x64.tar.xz && tar -xvf node-v16.16.0-linux-x64.tar.xz && mv node-v16.16.0-linux-x64 nodejs
RUN ln -s /opt/node/nodejs/bin/node /usr/local/bin/
RUN ln -s /opt/node/nodejs/bin/npm /usr/local/bin/
RUN npm config set registry http://registry.npm.taobao.org

COPY . /home/open-infra/web
RUN cd /home/open-infra/web && npm install
RUN cd /home/open-infra/web && npm run build



FROM nginx:1.20.0

# COPY ./deploy/test-login.html /usr/share/nginx/html/test-login.html

COPY --from=builder /home/open-infra/web/dist/ /usr/share/nginx/html/
RUN chmod -R 755 /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf


ENV RUN_USER nginx
ENV RUN_GROUP nginx
EXPOSE 8080
ENTRYPOINT ["nginx", "-g", "daemon off;"]

