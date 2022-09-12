import smtplib
from email.header import Header
from email.mime.text import MIMEText

smt_obj = smtplib.SMTP_SSL("smtp.qq.com", port=int(465))
smt_obj.login("353712216@qq.com", "")
email_receivers = ["tom_toworld@163.com"]
email_subject = "老朋友，再见面了"
message = MIMEText("Hello to world", 'html', 'utf-8')
message['From'] = "{0}<{1}>".format("朋友", "353712216@qq.com")
message['To'] = ';'.join(email_receivers)
message['Subject'] = Header(email_subject, 'utf-8')
a = smt_obj.sendmail("353712216@qq.com", email_receivers, message.as_string())
print(a)
