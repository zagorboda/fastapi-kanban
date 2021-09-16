from fastapi import UploadFile
from fastapi.exceptions import HTTPException

from starlette.status import (
    HTTP_400_BAD_REQUEST,
)

import aiofiles

from app.db.models import User


async def upload_image(*, file: UploadFile, user: User):
    if not file.content_type.startswith('image'):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Invalid image format')

    async with aiofiles.open(f'/usr/src/media/profile_pic/{user.username}.{file.content_type.split("/")[1]}', 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    return True
