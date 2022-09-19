import smtplib
from email.header import Header
from email.mime.text import MIMEText


# from django.test import TestCase


# Create your tests here.


def test_email():
    email_subject = "hello tom"
    email_content = "hello tom, I am TOm"
    email_receivers = ["tom_toworld@163.com"]
    sender_email = "infra@lists.osinfra.cn"
    sender_name = "infra"
    # server_address = "smtp.qq.com"
    server_address = "lists.osinfra.cn"
    server_port = int(465)
    message = MIMEText(email_content, 'html', 'utf-8')
    message['From'] = r'{0} <{1}>'.format(sender_name, sender_email)
    message['To'] = ';'.join(email_receivers)
    message['Subject'] = Header(email_subject, 'utf-8')
    smt_obj = smtplib.SMTP_SSL(server_address, port=int(server_port))
    smt_obj.login("", "")
    smt_obj.sendmail(sender_email, email_receivers, message.as_string())


if __name__ == '__main__':
    test_email()
