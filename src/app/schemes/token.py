from datetime import datetime, timedelta
from pydantic import EmailStr, BaseModel
from app.core.config import JWT_AUDIENCE, ACCESS_TOKEN_EXPIRE_MINUTES


class JWTMeta(BaseModel):
    aud: str = JWT_AUDIENCE
    iat: float = datetime.timestamp(datetime.utcnow())
    exp: float = datetime.timestamp(datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


class JWTCreds(BaseModel):
    """
    Identify users
    """

    sub: EmailStr
    username: str


class JWTPayload(JWTMeta, JWTCreds):
    """
    JWT Payload right before it's encoded - combine meta and username
    """

    pass


class AccessToken(BaseModel):
    access_token: str
    token_type: str
