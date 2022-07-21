FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /root/porch_space
WORKDIR /root/porch_space
COPY requirements.txt /root/porch_space/
RUN pip install -r /root/porch_space/requirements.txt
ADD open_infra /root/porch_space
ENTRYPOINT ["python3", "/root/porch_space/manage.py", "runserver", "0.0.0.0:80", "--noreload"]
EXPOSE 80