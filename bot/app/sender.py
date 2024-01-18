import smtplib
from email.mime.text import MIMEText
from random import randint
from os import getenv


def connect_to_mail():
    sender = 'n-i-2017@mail.ru'
    password = getenv('EMAIL_PASSWORD')
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    server.login(sender, password)

    return sender, server


def register_mail(receiver):
    sender, server = connect_to_mail()
    try:
        code = randint(000000, 999999)
        msg = MIMEText(f'Ваш код: {code}')
        msg['Subject'] = "Подтверждение почты"
        server.sendmail(sender, receiver, msg.as_string())

        return code
    except smtplib.SMTPDataError:
        return False

    except Exception as e:
        print(e)



def send_notification_mail(user_email, caption, fields) -> None:
    sender, server = connect_to_mail()
    try:
        msg = MIMEText(fields, 'html')
        msg['Subject'] = caption.replace('<b>', '').replace('</b>', '')
        server.sendmail(sender, user_email, msg.as_string())

    except smtplib.SMTPDataError:
        pass
