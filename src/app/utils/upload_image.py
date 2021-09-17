# from base64 import decodebytes

from fastapi import UploadFile
from fastapi.exceptions import HTTPException

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    # HTTP_413_REQUEST_ENTITY_TOO_LARGE
)

# import aiofiles
from PIL import Image, UnidentifiedImageError
# from io import BytesIO

from app.db.models import User


# DATA_CHUNK_SIZE = 1024
# # Max file size have been handled by web server
# MAX_IMG_SIZE = 1024 * 1024 * 5


async def upload_image(*, file: UploadFile, user: User):

    if not file.content_type.startswith('image'):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid image format')

    # Convert image to bytes to check image size.
    # # File upload size should be checked using web server or reverse proxy
    # image_bytes = await file.read()
    # if len(image_bytes) > MAX_IMG_SIZE:
    #     raise HTTPException(
    #         status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    #         detail=f'Image too large. Limit is {MAX_IMG_SIZE / (1024 * 1024)} Mb.'
    #     )

    try:
        img = Image.open(file.file)
    except UnidentifiedImageError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid image file or format')

    img.thumbnail((100, 100))
    img.save(f'/usr/src/media/profile_pic/{user.username}.jpg')

    # async with aiofiles.open(f'/usr/src/media/profile_pic/{user.username}.jpeg', 'wb') as out_file:
    #     while content := await img.read(DATA_CHUNK_SIZE):  # async read chunk
    #         await out_file.write(content)  # async write chunk

    return True
