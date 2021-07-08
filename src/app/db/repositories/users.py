from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr

from app.db import models
from app.schemes import user as user_scheme
from app.services import auth_service


class UsersRepository:
    def __init__(self):
        self.auth_service = auth_service

    async def get_all_users(self):
        return await models.User.query.gino.all()

    async def get_user_by_username(self, username: str):
        return await models.User.query.where(models.User.username == username).gino.first()

    async def get_user_by_email(self, email: EmailStr):
        return await models.User.query.where(models.User.email == email).gino.first()

    async def register_new_user(self, new_user: user_scheme.UserCreate):
        if await self.get_user_by_email(new_user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That email is already taken. Login with that email or register with another one."
            )

        if await self.get_user_by_username(new_user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That username is already taken. Please try another one."
            )

        user_password_update = self.auth_service.create_salt_and_hashed_password(plaintext_password=new_user.password)
        new_user_params = new_user.copy(update=user_password_update.dict())

        return await models.User.create(**new_user_params.dict())

    async def authenticate_user(self, *, username: str, password: str) -> Optional[user_scheme.User]:
        user = await self.get_user_by_username(username=username)
        if not user:
            return None
        if not self.auth_service.verify_password(password=password, salt=user.salt, hashed_pw=user.password):
            return None
        return user
