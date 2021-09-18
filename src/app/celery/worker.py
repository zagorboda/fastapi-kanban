# import aiofiles
import os

from celery import Celery
# from fastapi import UploadFile

# from app.db.models import User

from fastapi.exceptions import HTTPException

from starlette.status import (
    HTTP_400_BAD_REQUEST
)

from PIL import Image, UnidentifiedImageError
# from fastapi import UploadFile
from io import BytesIO

# import base64


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

    # file = base64.b64decode(file)
    # file = file.encode("utf-8")

    # if not file.content_type.startswith('image'):
    #     raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid image format')

    # Convert image to bytes to check image size.
    # # File upload size should be checked using web server or reverse proxy
    # image_bytes = await file.read()
    # if len(image_bytes) > MAX_IMG_SIZE:
    #     raise HTTPException(
    #         status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    #         detail=f'Image too large. Limit is {MAX_IMG_SIZE / (1024 * 1024)} Mb.'
    #     )

    try:
        img = Image.open(BytesIO(bytes.fromhex(file)))
    except UnidentifiedImageError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid image file or format')

    img.thumbnail((100, 100))
    img.save(f'/usr/src/media/profile_pic/{username}.jpg')

    # async with aiofiles.open(f'/usr/src/media/profile_pic/{user.username}.jpeg', 'wb') as out_file:
    #     while content := await img.read(DATA_CHUNK_SIZE):  # async read chunk
    #         await out_file.write(content)  # async write chunk

    return file
