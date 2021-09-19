import aiofiles
import os

from fastapi import UploadFile

from app.celery.worker import upload_image_task, send_sign_up_email, delete_image_task
from app.core.config import PROFILE_PICTURE_PATH, MEDIA_PATH
from app.db.models import User


async def upload_image(*, file: UploadFile, user: User):
    image_bytes = await file.read()
    hex_bytes = image_bytes.hex()
    image_async_res = upload_image_task.delay(username=user.username, file=hex_bytes)

    return image_async_res


async def delete_image(*, user: User):
    delete_result = delete_image_task.delay(username=user.username)

    print(delete_result)
    print(delete_result.get())

    return delete_result
