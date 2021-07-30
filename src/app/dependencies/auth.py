from typing import Optional, Union


from fastapi import Depends, HTTPException, Request
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from starlette.status import (
    HTTP_401_UNAUTHORIZED,
)

from app.core.config import SECRET_KEY, API_PREFIX
from app.db.repositories.users import UsersRepository
from app.db.models import User
from app.schemes import user as user_scheme
from app.services import auth_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/users/login/token/")


async def get_user_from_token(
    *,
    token: str = Depends(oauth2_scheme),
) -> Optional[User]:
    try:
        username = auth_service.get_username_from_token(token=token, secret_key=str(SECRET_KEY))
        user = await UsersRepository().get_user_by_username(username=username)
    except Exception as e:
        raise e
    return user


def get_current_active_user(current_user: User = Depends(get_user_from_token)) -> Optional[User]:
    if not current_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="No authenticated user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not an active user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_current_active_or_unauthenticated_user(request: Request) -> Union[None, User]:
    """
    Return user object if request user if authenticated, else return none.
    """
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)

    if not authorization or scheme.lower() != "bearer":
        return None

    username = auth_service.get_username_from_token(token=token, secret_key=str(SECRET_KEY))

    user = await UsersRepository().get_user_by_username(username=username)

    return user
