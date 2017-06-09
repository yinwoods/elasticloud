# coding:utf-8
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from elasticloud import settings


def send(receiver, subject, text):
    ret = True
    try:
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = formataddr(["E-CLOUD", settings.EMAIL_ADDRESS])
        msg['To'] = formataddr(["", receiver])
        msg['Subject'] = subject
        server = smtplib.SMTP("smtp.163.com", 25)
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_ADDRESS, [receiver, ], msg.as_string())
        server.quit()
    except Exception as e:
        ret = False
    return ret
