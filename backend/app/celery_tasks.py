from typing import List
from celery import Celery
from app.mail import create_message, mail
from asgiref.sync import async_to_sync
c_app = Celery()

c_app.config_from_object("app.core.config")


@c_app.task()
def send_email(recipients : List[str], subject : str, body : str):
    message = create_message(
        recipients=recipients,
        subject=subject,
        body=body
    )
    async_to_sync(mail.send_message)(message)