from fastapi import APIRouter, Path, Body, Depends
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
from app.dependencies.auth import get_current_active_user
from app.schemes import user as user_schemas
from app.services import auth_service
from app.schemes.token import AccessToken

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# @router.get("/me/", response_model=user_schemas.User, name="users:get-current-user")
# async def get_currently_authenticated_user(current_user: user_schemas.User = Depends(get_current_active_user)) -> user_schemas.User:
#     return current_user


@router.post("/login/token/", response_model=AccessToken, name="users:login-email-and-password")
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
    access_token = AccessToken(access_token=auth_service.create_access_token_for_user(user=user_schemas.User(**user.to_dict())), token_type="bearer")
    return access_token


@router.get("/{username}", response_model=user_schemas.UserPublic, name="users:get-user")
async def get_user_by_username(username: str = Path(..., min_length=3, regex="^[a-zA-Z0-9_-]+$")) -> user_schemas.User:
    user = await UsersRepository().get_user_by_username(username)
    if user is None:
        return None
    return user_schemas.User(**user.to_dict())


@router.post("/", response_model=user_schemas.User, name="users:register-new-user", status_code=HTTP_201_CREATED)
async def register_new_user(new_user: user_schemas.UserCreate = Body(..., embed=True)) -> user_schemas.User:
    created_user = await UsersRepository().register_new_user(new_user)
    print(created_user)
    access_token = AccessToken(
        access_token=auth_service.create_access_token_for_user(user=user_schemas.User(**created_user.to_dict())), token_type="bearer"
    )

    return user_schemas.User(**created_user.to_dict(), access_token=access_token)


# @router.put("/me/", response_model=ProfilePublic, name="profiles:update-own-profile")
# async def update_own_profile(profile_update: ProfileUpdate = Body(..., embed=True)) -> ProfilePublic:
#     return None
