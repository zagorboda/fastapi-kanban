import aiofiles
import os

from fastapi import UploadFile

from app.celery.worker import upload_image_task, send_sign_up_email, delete_image_task
from app.db.models import User


async def upload_image(*, file: UploadFile, user: User):
    image_bytes = await file.read()
    hex_bytes = image_bytes.hex()
    image_async_res = upload_image_task.delay(username=user.username, file=hex_bytes)

    return image_async_res


async def delete_image(*, user: User):
    delete_result = delete_image_task.delay(username=user.username)

    return delete_result
