from typing import Optional
from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    """
    Models to create user
    """
    email: EmailStr
    password: constr(min_length=7, max_length=100)
    username: constr(min_length=3, max_length=100, regex="^[a-zA-Z0-9_-]+$")


class UserUpdate(BaseModel):
    """
    Model to update user email and/or username
    """
    email: Optional[EmailStr]
    username: Optional[constr(min_length=3, regex="^[a-zA-Z0-9_-]+$")]


class InputPasswordUpdate(BaseModel):
    """
    Model to get new user password
    """
    password: constr(min_length=7, max_length=100)


class UserPasswordUpdate(BaseModel):
    """
    Model to change user password
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

    class Config:
        orm_mode = True


class UserPublic(BaseModel):
    """
    Models to return public user information
    """
    username: str
