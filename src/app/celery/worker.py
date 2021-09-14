import os
import time

from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")


def mock_up_send_email(email, message):
    print(f'Sending sign up email to {email}')

    # Code to send email (using some libs like fastapi-mail)
    # ...


@celery.task(name="send_email", soft_time_limit=60)
def send_sign_up_email(*, email: str):
    message = 'You just signed up. Please, confirm email...'

    mock_up_send_email(email, message)

    return True
