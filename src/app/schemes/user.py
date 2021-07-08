from typing import Optional
from pydantic import BaseModel, EmailStr, constr

from app.schemes.token import AccessToken


class UserCreate(BaseModel):
    """
    Models for creating user
    """
    email: EmailStr
    password: constr(min_length=7, max_length=100)
    username: constr(min_length=3, max_length=100, regex="^[a-zA-Z0-9_-]+$")


class UserUpdate(BaseModel):
    """
    Users are allowed to update their email and/or username
    """
    email: Optional[EmailStr]
    username: Optional[constr(min_length=3, regex="^[a-zA-Z0-9_-]+$")]


class UserPasswordUpdate(BaseModel):
    """
    Users can change their password
    """
    password: constr(min_length=7, max_length=100)
    salt: str


class User(BaseModel):
    """
    Model to return user information
    """
    id: int
    is_active: bool = True
    is_superuser: bool = False
    username: str
    email: EmailStr
    # access_token: Optional[AccessToken]
    # boards: "List[Board]" = []

    class Config:
        orm_mode = True


class UserPublic(BaseModel):
    """
    Public user information
    """
    username: str
