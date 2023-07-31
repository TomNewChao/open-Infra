FROM centos:7

MAINTAINER TomNewChao<353712216@qq.com>
ENV PYTHONUNBUFFERED 1

RUN mkdir /opt/open_infra
WORKDIR /opt/open_infra
COPY . /opt/open_infra/
COPY ./docker-entrypoint.sh /usr/local/bin/
RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
RUN cp /opt/open_infra/build/kubernetes.repo /etc/yum.repos.d/ && chmod 755 /etc/yum.repos.d/kubernetes.repo
RUN yum update -y && yum install -y gcc gcc-c++ python3 python3-pip python3-devel nmap kubectl git mysql
RUN pip3 install -r /opt/open_infra/requirements.txt
RUN tar -zxvf /opt/open_infra/build/kustomize_v3.6.1_linux_amd64.tar.gz -C /usr/bin/
RUN mkdir /var/log/open-infra/
ENV LANG=en_US.UTF-8
ENV PYTHONPATH=/opt/open_infra
ENTRYPOINT ["docker-entrypoint.sh"]
#CMD ["uwsgi", "--ini", "/opt/open_infra/uwsgi.ini"]
CMD ["python3", "manage.py", "runserver","0.0.0.0:80", "--noreload"]
EXPOSE 80