import aiofiles
import os

from celery import Celery
from fastapi import UploadFile

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


@celery.task(name="write_file_on_disk", soft_time_limit=60)
def write_file_on_disk(*, file: UploadFile):
    # async with aiofiles.open(f'app/media/{file.filename}', 'wb') as out_file:
    #     while content := await file.read(1024):  # async read chunk
    #         await out_file.write(content)  # async write chunk

    return True
