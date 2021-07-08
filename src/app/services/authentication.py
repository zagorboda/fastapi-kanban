import jwt
import bcrypt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.core.config import SECRET_KEY, JWT_ALGORITHM, JWT_AUDIENCE, JWT_TOKEN_PREFIX, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemes import token as token_sheme, user as user_scheme

from typing import Optional
from fastapi import HTTPException, status
from pydantic import ValidationError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# class AuthException(BaseException):from app.db.schemas import user
#     pass


class AuthService:
    def create_salt_and_hashed_password(self, *, plaintext_password: str) -> user_scheme.UserPasswordUpdate:
        salt = self.generate_salt()
        hashed_password = self.hash_password(password=plaintext_password, salt=salt)
        return user_scheme.UserPasswordUpdate(salt=salt, password=hashed_password)

    def generate_salt(self) -> str:
        return bcrypt.gensalt().decode()

    def hash_password(self, *, password: str, salt: str) -> str:
        return pwd_context.hash(password + salt)

    def verify_password(self, *, password: str, salt: str, hashed_pw: str) -> bool:
        return pwd_context.verify(password + salt, hashed_pw)

    def create_access_token_for_user(
            self,
            *,
            user: user_scheme.User,
            secret_key: str = str(SECRET_KEY),
            audience: str = JWT_AUDIENCE,
            expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> str:
        if not user or not isinstance(user, user_scheme.User):
            return None
        jwt_meta = token_sheme.JWTMeta(
            aud=audience,
            iat=datetime.timestamp(datetime.utcnow()),
            exp=datetime.timestamp(datetime.utcnow() + timedelta(minutes=expires_in)),
        )
        jwt_creds = token_sheme.JWTCreds(sub=user.email, username=user.username)
        token_payload = token_sheme.JWTPayload(
            **jwt_meta.dict(),
            **jwt_creds.dict(),
        )
        access_token = jwt.encode(token_payload.dict(), secret_key, algorithm=JWT_ALGORITHM)
        return access_token

    def get_username_from_token(self, *, token: str, secret_key: str) -> Optional[str]:
        try:
            decoded_token = jwt.decode(token, str(secret_key), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])
            payload = token_sheme.JWTPayload(**decoded_token)
        except (jwt.PyJWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload.username
