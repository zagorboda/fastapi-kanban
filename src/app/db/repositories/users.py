from typing import Optional

from fastapi import HTTPException, status, Body
from pydantic import EmailStr

from app.core import config
from app.db import models
from app.schemes import user as user_schema
from app.services import auth_service


class UsersRepository:
    def __init__(self):
        self.auth_service = auth_service

    async def get_all_users(self):
        return await models.User.query.gino.all()

    async def get_user_profile_url(self, username: str):
        return f'{config.BASE_URL}{config.API_PREFIX}/users/user/{username}'

    async def get_user_by_username(self, username: str):
        return await models.User.query.where(models.User.username == username).gino.first()

    async def get_user_by_email(self, email: EmailStr):
        return await models.User.query.where(models.User.email == email).gino.first()

    async def register_new_user(self, new_user: user_schema.UserCreate):
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

    async def authenticate_user(self, *, username: str, password: str) -> Optional[user_schema.User]:
        user = await self.get_user_by_username(username=username)
        if not user:
            return None
        if not self.auth_service.verify_password(password=password, salt=user.salt, hashed_pw=user.password):
            return None
        return user

    async def update_profile(self, *,
        current_user: user_schema.User,
        profile_update: user_schema.UserUpdate,
    ) -> Optional[models.User]:

        if profile_update.username:
            # check if new username exists
            user_with_new_username = await self.get_user_by_username(profile_update.username)
            if user_with_new_username and user_with_new_username.id != current_user.id:
                raise ValueError(f"Username {profile_update.username} already taken")

        if profile_update.email:
            # check if new email exists
            user_with_new_email = await self.get_user_by_email(profile_update.email)
            if user_with_new_email and user_with_new_email.id != current_user.id:
                raise ValueError(f"Email {profile_update.email} already taken")

        # filter None value in optional fields
        patched_fields = {k: v for k, v in profile_update.dict().items() if v is not None}
        if patched_fields:
            await current_user.update(**patched_fields).apply()

        return current_user

    async def update_password(self, *,
        current_user: user_schema.User,
        password_update: user_schema.InputPasswordUpdate,
    ) -> Optional[models.User]:

        updated_password_and_salt = self.auth_service.create_salt_and_hashed_password(plaintext_password=password_update.password)
        await current_user.update(**dict(updated_password_and_salt)).apply()

        return current_user


user_repo = UsersRepository()
