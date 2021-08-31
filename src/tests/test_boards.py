import json
import pytest

from app.core import config as app_config
from app.db.database import db
from app.db.repositories.users import UsersRepository
from app.db.repositories.boards import BoardsRepository
from app.schemes import user as user_schema
from app.schemes import board as board_schema


pytestmark = pytest.mark.asyncio


class TestCreate:
    async def test_with_valid_data(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            # create new user
            user_payload = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_payload)
            )

            # get token
            token_response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            access_token = token_response.json()['access_token']

            # create board
            board_data = {'board': {'title': 'title', 'public': True}}

            response = await client.post(
                "/api/boards",
                content=json.dumps(board_data),
                headers={'Authorization': f'Bearer {access_token}'}
            )


            owner = await UsersRepository().get_user_by_username('username')

            await client.aclose()

        assert response.status_code == 201
        assert response.json()['title'] == board_data['board']['title']
        assert response.json()['public'] is True

    async def test_default_value(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            # create new user
            user_payload = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_payload)
            )

            owner = await UsersRepository().get_user_by_username('username')

            # get token
            token_response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            access_token = token_response.json()['access_token']

            # create board
            board_data = {'board': {'title': 'title'}}

            response = await client.post(
                "/api/boards",
                content=json.dumps(board_data),
                headers={'Authorization': f'Bearer {access_token}'}
            )

            owner = await UsersRepository().get_user_by_username('username')

            await client.aclose()

        assert response.status_code == 201
        assert response.json()['title'] == board_data['board']['title']
        assert response.json()['owner_id'] == owner.id
        assert response.json()['public'] is False

    async def test_invalid_data(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            # create new user
            user_payload = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_payload)
            )

            owner = await UsersRepository().get_user_by_username('username')

            # get token
            token_response = await client.post(
                "/api/users/login/token",
                data={'username': 'username', 'password': 'password'}
            )

            access_token = token_response.json()['access_token']

            # create board
            board_data = {'board': {'public': 'test'}}

            response = await client.post(
                "/api/boards",
                content=json.dumps(board_data),
                headers={'Authorization': f'Bearer {access_token}'}
            )

            await client.aclose()

        assert response.status_code == 422

    async def test_unauthenticated_user(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            # create board
            board_data = {'board': {'public': 'test'}}

            response = await client.post(
                "/api/boards",
                content=json.dumps(board_data)
            )

            await client.aclose()

        assert response.status_code == 401


class TestGetAll:
    async def test_empty_list(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):

            response = await client.get(
                "/api/boards"
            )

            await client.aclose()

        assert response.status_code == 200
        assert response.json() == []

    async def test_list(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            user_payload = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            user = await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_payload)
            )

            for i in range(3):
                await BoardsRepository().create_new_board(
                    board=board_schema.BoardCreate(**{'title': f'test{i}', 'public': True}),
                    owner=user
                )

            response = await client.get(
                "/api/boards"
            )

            await client.aclose()

        assert response.status_code == 200
        assert len(response.json()) == 3

    async def test_list_with_different_public_boards(self, client):
        async with db.with_bind(app_config.TEST_DB_DSN):
            user_payload = {'email': 'user@example.com', 'username': 'username', 'password': 'password'}
            user = await UsersRepository().register_new_user(
                user_schema.UserCreate(**user_payload)
            )

            for i in range(5):
                await BoardsRepository().create_new_board(
                    board=board_schema.BoardCreate(**{'title': f'test{i}', 'public': i % 2}),
                    owner=user
                )

            response = await client.get(
                "/api/boards"
            )

            await client.aclose()

        assert response.status_code == 200
        assert len(response.json()) == 2
