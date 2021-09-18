# from base64 import decodebytes

from fastapi import UploadFile
from fastapi.exceptions import HTTPException

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    # HTTP_413_REQUEST_ENTITY_TOO_LARGE
)

# import aiofiles
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import base64

from app.db.models import User
from app.celery.worker import upload_image_task, send_sign_up_email
from celery.result import AsyncResult

# DATA_CHUNK_SIZE = 1024
# # Max file size have been handled by web server
# MAX_IMG_SIZE = 1024 * 1024 * 5


async def upload_image(*, file: UploadFile, user: User):

    image_bytes = await file.read()
    h = image_bytes.hex()
    i = upload_image_task.delay(username=user.username, file=h)

    # print(str(base64.b64encode(image_bytes)))
    # print(base64.b64encode(image_bytes))
    # i = send_sign_up_email.delay(email='123')
    # img = Image.open(BytesIO(bytes.fromhex(h)))

    # i = upload_image_task.delay(username=user.username, file=image_bytes.decode("utf-8"))
    # i = upload_image_task.delay(username=user.username, file=str(base64.b64encode(image_bytes)))
    # print(i.id)
    # print(i.get())

    # res = AsyncResult(i.id)
    # while res.ready() is not True:
    #     time.sleep(2)
    #     print(res.ready())
    #
    # try:
    #     img = Image.open(BytesIO(base64.b64decode(base64.b64encode(image_bytes))))
    # except UnidentifiedImageError:
    #     raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid image file or format')

    # upload_image_task.delay(username=user.username, file=image_bytes)

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

    # try:
    #     img = Image.open(file.file)
    # except UnidentifiedImageError:
    #     raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid image file or format')
    #
    # img.thumbnail((100, 100))
    # img.save(f'/usr/src/media/profile_pic/{user.username}.jpg')

    # async with aiofiles.open(f'/usr/src/media/profile_pic/{user.username}.jpeg', 'wb') as out_file:
    #     while content := await img.read(DATA_CHUNK_SIZE):  # async read chunk
    #         await out_file.write(content)  # async write chunk

    return True
