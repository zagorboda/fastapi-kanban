import os

from celery import Celery
from fastapi.exceptions import HTTPException
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from starlette.status import (
    HTTP_400_BAD_REQUEST
)

from app.core.config import PROFILE_PICTURE_PATH, MEDIA_PATH

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


@celery.task(name="upload_image_task", soft_time_limit=60)
def upload_image_task(*, file: str, username: str):
    try:
        img = Image.open(BytesIO(bytes.fromhex(file)))
    except UnidentifiedImageError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid image file or format')

    img.thumbnail((100, 100))
    img.save(f'{PROFILE_PICTURE_PATH}{username}.jpg')

    return username
