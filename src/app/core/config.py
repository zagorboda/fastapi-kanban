import os
import pathlib

from sqlalchemy.engine.url import URL, make_url
from starlette.config import Config
from starlette.datastructures import Secret


env_path = os.path.join(pathlib.Path(__file__).parent.absolute(), '.env')

config = Config(env_path)
PROJECT_NAME = "Kanban"
VERSION = "1.0.0"
API_PREFIX = "/api"
BASE_URL = 'http://127.0.0.1:8000'


# openssl rand -hex 32
SECRET_KEY = config("SECRET_KEY", cast=Secret, default=None)

ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    cast=int,
    default=60
)
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
JWT_AUDIENCE = config("JWT_AUDIENCE", cast=str, default='fastapi:auth')
JWT_TOKEN_PREFIX = config("JWT_TOKEN_PREFIX", cast=str, default="Bearer")

# TESTING = config("TESTING", cast=bool, default=False)

# DEBUG = 1  # (0, 1, 2)

DB_DRIVER = config("DB_DRIVER", default="postgresql")
DB_HOST = config("DB_HOST", default=None)
DB_PORT = config("DB_PORT", cast=int, default=5432)
DB_USER = config("DB_USER", default=None)
DB_PASSWORD = config("DB_PASSWORD", cast=Secret, default=None)
DB_NAME = config("DB_NAME", default=None)

# if TESTING:

DB_DSN = config(
    "DB_DSN",
    cast=make_url,
    default=URL(
        drivername=DB_DRIVER,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    ),
)

DB_POOL_MIN_SIZE = config("DB_POOL_MIN_SIZE", cast=int, default=1)
DB_POOL_MAX_SIZE = config("DB_POOL_MAX_SIZE", cast=int, default=16)
DB_ECHO = config("DB_ECHO", cast=bool, default=False)
DB_SSL = config("DB_SSL", default=None)
DB_USE_CONNECTION_FOR_REQUEST = config(
    "DB_USE_CONNECTION_FOR_REQUEST", cast=bool, default=True
)
DB_RETRY_LIMIT = config("DB_RETRY_LIMIT", cast=int, default=1)
DB_RETRY_INTERVAL = config("DB_RETRY_INTERVAL", cast=int, default=1)

TEST_DB_DRIVER = config("TEST_DB_DRIVER", default="postgresql")
TEST_DB_HOST = config("TEST_DB_HOST", default='db')
TEST_DB_PORT = config("TEST_DB_PORT", cast=int, default=5432)
TEST_DB_USER = config("TEST_DB_USER", default='admin')
TEST_DB_PASSWORD = config("TEST_DB_PASSWORD", cast=Secret, default='admin')
TEST_DB_NAME = config("TEST_DB_NAME", default='test')

TEST_DB_DSN = config(
    "TEST_DB_DSN",
    cast=make_url,
    default=URL(
        drivername=TEST_DB_DRIVER,
        username=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        host=TEST_DB_HOST,
        port=TEST_DB_PORT,
        database=TEST_DB_NAME,
    ),
)
