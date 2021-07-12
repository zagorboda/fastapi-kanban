import json
import pytest

from app.core import config as app_config
from app.db.database import db
from app.db.repositories.users import UsersRepository
from app.schemes import user as user_schema

engine = db.with_bind(app_config.TEST_DB_DSN)


def get_engine():
    return engine


pytestmark = pytest.mark.asyncio


class TestSingUp:
    async def test_with_valid_data(self, client):
        payload = {'new_user': {'email': 'user@example.com', 'username': 'username', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN):
            response = await client.post("/api/users", content=json.dumps(payload))
            await client.aclose()

            users_in_db = await UsersRepository().get_all_users()

        assert len(users_in_db) == 1
        assert response.status_code == 201

    async def test_with_invalid_username(self, client):
        payload = {'new_user': {'email': 'user@example.com', 'username': 'ab', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN):
            response = await client.post("/api/users", content=json.dumps(payload))
            await client.aclose()

        assert response.status_code == 422

    async def test_with_invalid_email(self, client):
        payload = {'new_user': {'email': 'invalid.com', 'username': 'username', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN):
            response = await client.post("/api/users", content=json.dumps(payload))
            await client.aclose()

        assert response.status_code == 422

    async def test_with_duplicate_email(self, client):
        payload1 = {'new_user': {'email': 'user@example.com', 'username': 'username', 'password': 'fake_password'}}
        payload2 = {'new_user': {'email': 'user@example.com', 'username': 'username1', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN):
            await client.post("/api/users", content=json.dumps(payload1))
            response = await client.post("/api/users", content=json.dumps(payload2))
            await client.aclose()

        assert response.status_code == 400

    async def test_with_duplicate_username(self, client):
        payload1 = {'new_user': {'email': 'user1@example.com', 'username': 'username', 'password': 'fake_password'}}
        payload2 = {'new_user': {'email': 'user2@example.com', 'username': 'username', 'password': 'fake_password'}}

        async with db.with_bind(app_config.TEST_DB_DSN):
            await client.post("/api/users", content=json.dumps(payload1))
            response = await client.post("/api/users", content=json.dumps(payload2))
            await client.aclose()

        assert response.status_code == 400

    async def test_without_password(self, client):
        payload = {'new_user': {'email': 'user1@example.com', 'username': 'username', 'password': ''}}

        async with db.with_bind(app_config.TEST_DB_DSN):
            response = await client.post("/api/users", content=json.dumps(payload))
            await client.aclose()

        assert response.status_code == 422


class TestLogin:
    async def test_valid_data(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):

            await UsersRepository().register_new_user(
                user_schema.UserCreate(**{'email': 'user@example.com', 'username': 'username', 'password': 'password'})
            )

            response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            await client.aclose()

        assert response.status_code == 200
        assert 'access_token' in response.json()
        assert 'token_type' in response.json()

    async def test_invalid_data(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            await client.aclose()

        assert response.status_code == 401


class TestSelfUser:
    async def test_authenticated_user(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**{'email': 'user@example.com', 'username': 'username', 'password': 'password'})
            )

            response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            access_token = response.json()['access_token']

            response = await client.get("/api/users/me", headers={'Authorization': f'Bearer {access_token}'})

            await client.aclose()

        assert response.status_code == 200

    async def test_unauthenticated_user(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**{'email': 'user@example.com', 'username': 'username', 'password': 'password'})
            )

            response = await client.get("/api/users/me")

            await client.aclose()

        assert response.status_code == 401


class TestGetUser:
    async def test_existing_user(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            user_data = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_data)
            )

            response = await client.get(f'/api/users/user/{user_data["username"]}')

            await client.aclose()

        assert response.status_code == 200
        assert response.json()['username'] == user_data["username"]

    async def test_not_existing_user(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            response = await client.get(f'/api/users/user/username')

            await client.aclose()

        assert response.status_code == 404


class TestProfileUpdate:
    async def test_valid_data(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            user_data = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_data)
            )

            response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            access_token = response.json()['access_token']

            response = await client.patch(
                '/api/users/me',
                content=json.dumps({"profile_update": {'username': 'new_username', 'email': 'new_email@example.com'}}),
                headers={'Authorization': f'Bearer {access_token}'}
            )

            await client.aclose()

        assert response.status_code == 200

    async def test_invalid_email(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            user_data = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_data)
            )

            response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            access_token = response.json()['access_token']

            response = await client.patch(
                '/api/users/me',
                content=json.dumps({"profile_update": {'email': 'new_email'}}),
                headers={'Authorization': f'Bearer {access_token}'}
            )

            await client.aclose()

        assert response.status_code == 422

    async def test_empty(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            user_data = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_data)
            )

            response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            access_token = response.json()['access_token']

            response = await client.patch(
                '/api/users/me',
                content=json.dumps({"profile_update": {}}),
                headers={'Authorization': f'Bearer {access_token}'}
            )

            await client.aclose()

        assert response.status_code == 200


class TestPasswordUpdate:
    async def test_valid_data(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            user_data = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_data)
            )

            user = await UsersRepository().get_user_by_username('username')
            user = user.to_dict()
            old_password, old_salt = user['password'], user['salt']

            response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            access_token = response.json()['access_token']

            response = await client.patch(
                '/api/users/me/password_update',
                content=json.dumps({"password_update": {'password': 'new_password'}}),
                headers={'Authorization': f'Bearer {access_token}'}
            )

            user = await UsersRepository().get_user_by_username('username')
            user = user.to_dict()
            new_password, new_salt = user['password'], user['salt']

            await client.aclose()

        assert response.status_code == 200
        assert old_salt != new_salt
        assert old_password != new_password
