from app.core import config
from app.db import models
from app.db.database import db
from app.schemes import card as card_schema
from app.services import auth_service


class CardsRepository:
    def __init__(self):
        self.auth_service = auth_service

    async def get_card_url(self, board_id: int, list_id: int, card_id: int):
        return f'{config.BASE_URL}{config.API_PREFIX}/boards/{board_id}/lists/{list_id}/card/{card_id}'

    async def get_card(self, card_id: int):
        return await models.Card.get(card_id)

    async def create_new_card(self, *, card: card_schema.CardCreate, list_id: int, user_id: int):
        return await models.Card.create(**card.dict(), **{'list_id': list_id, 'last_change_by_id': user_id})

    async def get_list_cards(self, *, list_id: int, offset=0, limit=25):
        if not limit:
            limit = 25

        async with db.transaction():
            cursor = await models.Card.query.where(models.Card.list_id == list_id).gino.iterate()
            if offset:
                await cursor.forward(offset)
            cards = await cursor.many(limit)
        return cards


card_repo = CardsRepository()
