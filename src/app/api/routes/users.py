from fastapi import APIRouter, Path, Body, Depends, HTTPException
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from app.db.repositories.users import UsersRepository
from app.db.models import User
from app.dependencies.auth import get_current_active_user
from app.schemes import user as user_schema
from app.services import auth_service
from app.schemes.token import AccessToken

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/me/", name="user:get-current-user")
async def get_currently_authenticated_user(current_user: User = Depends(get_current_active_user)) -> User:
    return user_schema.UserPublic(**current_user.to_dict())


@router.post("/login/token/", response_model=AccessToken, name="user:login-email-and-password")
async def user_login_with_email_and_password(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
) -> AccessToken:
    user = await UsersRepository().authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Authentication was unsuccessful.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AccessToken(access_token=auth_service.create_access_token_for_user(user=user_schema.User(**user.to_dict())), token_type="bearer")
    return access_token


@router.get("/user/{username}", response_model=user_schema.UserPublic, name="user:get-user-by-username")
async def get_user_by_username(username: str = Path(..., min_length=3, regex="^[a-zA-Z0-9_-]+$")) -> user_schema.User:
    user = await UsersRepository().get_user_by_username(username)
    if user is None:
        return None
    return user_schema.User(**user.to_dict())


@router.post("/", response_model=user_schema.User, name="users:register-new-user", status_code=HTTP_201_CREATED)
async def register_new_user(new_user: user_schema.UserCreate = Body(..., embed=True)) -> user_schema.User:
    created_user = await UsersRepository().register_new_user(new_user)

    access_token = AccessToken(
        access_token=auth_service.create_access_token_for_user(user=user_schema.User(**created_user.to_dict())), token_type="bearer"
    )

    return user_schema.User(**created_user.to_dict(), access_token=access_token)


@router.put("/me/", name="profiles:update-own-profile")
async def update_own_profile(
    profile_update: user_schema.UserUpdate = Body(..., embed=True),
    current_user: user_schema.User = Depends(get_current_active_user)
) -> user_schema.User:

    try:
        updated_user = await UsersRepository().update_profile(profile_update=profile_update, current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return user_schema.User(**updated_user.to_dict())


@router.put("/me/password_update", name="profiles:update-own-password")
async def update_password(
    password_update: user_schema.InputPasswordUpdate = Body(..., embed=True),
    current_user: user_schema.User = Depends(get_current_active_user)
) -> user_schema.User:
    return await UsersRepository().update_password(current_user=current_user, password_update=password_update)
