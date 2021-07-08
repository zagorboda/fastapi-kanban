import json
import pytest

from app.core import config as app_config
from app.db.database import db
from app.db.repositories import users as user_repo


engine = db.with_bind(app_config.TEST_DB_DSN)


def get_engine():
    return engine


pytestmark = pytest.mark.asyncio


class TestSingUpRoute:
    async def test_with_valid_data(self, client):
        payload = {'new_user': {'email': 'user@example.com', 'username': 'username', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN) as gino_engine:
            response = await client.post("/api/users", content=json.dumps(payload))
            await client.aclose()

            users_in_db = await user_repo.UsersRepository().get_all_users()

        assert len(users_in_db) == 1
        assert response.status_code == 201

    async def test_with_invalid_username(self, client):
        payload = {'new_user': {'email': 'user@example.com', 'username': 'ab', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN) as gino_engine:
            response = await client.post("/api/users", content=json.dumps(payload))
            await client.aclose()

        assert response.status_code == 422

    async def test_with_invalid_email(self, client):
        payload = {'new_user': {'email': 'invalid.com', 'username': 'username', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN) as gino_engine:
            response = await client.post("/api/users", content=json.dumps(payload))
            await client.aclose()

        assert response.status_code == 422

    async def test_with_duplicate_email(self, client):
        payload1 = {'new_user': {'email': 'user@example.com', 'username': 'username', 'password': 'fake_password'}}
        payload2 = {'new_user': {'email': 'user@example.com', 'username': 'username1', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN) as gino_engine:
            await client.post("/api/users", content=json.dumps(payload1))
            response = await client.post("/api/users", content=json.dumps(payload2))
            await client.aclose()

        assert response.status_code == 400

    async def test_with_duplicate_username(self, client):
        payload1 = {'new_user': {'email': 'user1@example.com', 'username': 'username', 'password': 'fake_password'}}
        payload2 = {'new_user': {'email': 'user2@example.com', 'username': 'username', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN) as gino_engine:
            await client.post("/api/users", content=json.dumps(payload1))
            response = await client.post("/api/users", content=json.dumps(payload2))
            await client.aclose()

        assert response.status_code == 400

    async def test_without_password(self, client):
        payload = {'new_user': {'email': 'user1@example.com', 'username': 'username', 'password': ''}}

        async with db.with_bind(app_config.TEST_DB_DSN) as gino_engine:
            response = await client.post("/api/users", content=json.dumps(payload))
            await client.aclose()

        assert response.status_code == 422
