from fastapi_mail import MessageType
from fastapi_mail import MessageSchema
from typing import List
from fastapi_mail import FastMail, ConnectionConfig
from app.core.config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

mail = FastMail(config=mail_config)

def create_message(recipients : List[str], subject : str, body : str):
    message = MessageSchema(recipients=recipients, subject=subject, body=body, subtype=MessageType.html)

    return message