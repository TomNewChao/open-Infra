FROM centos:7

MAINTAINER TomNewChao<353712216@qq.com>
ENV PYTHONUNBUFFERED 1

RUN mkdir /opt/open_infra
WORKDIR /opt/open_infra
COPY . /opt/open_infra/

RUN yum install -y gcc-c++
RUN yum install -y python3
RUN yum install -y python3-pip
RUN yum install -y python3-devel
RUN yum install -y java-1.8.0-openjdk*
RUN yum install -y nmap
RUN pip3 install -r /opt/open_infra/requirements.txt
COPY ./docker-entrypoint.sh /usr/local/bin/
RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
RUN mkdir /var/log/open-infra/


ENV LANG=en_US.UTF-8
ENV PYTHONPATH=/opt/open_infra
ENTRYPOINT ["docker-entrypoint.sh"]
#CMD ["uwsgi", "--ini", "/opt/open_infra/uwsgi.ini"]
CMD ["python3", "manage.py", "runserver","0.0.0.0:80", "--noreload"]
EXPOSE 80