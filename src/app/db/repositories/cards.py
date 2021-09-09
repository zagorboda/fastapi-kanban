import datetime

from fastapi import HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)

from app.core import config
from app.db import models, enums
from app.db.database import db
from app.schemes import card as card_schema
from app.services import auth_service


class CardsRepository:
    def __init__(self):
        self.auth_service = auth_service

    async def get_card_url(self, board_id: int, list_id: int, card_id: int):
        return f'{config.BASE_URL}{config.API_PREFIX}/boards/{board_id}/lists/{list_id}/card/{card_id}'

    async def get_card_by_id(self, card_id: int):
        return await models.Card.get(card_id)

    async def get_card_by_id_and_check_list_foreign_key(self, card_id: int, lst: models.List):
        card = await models.Card.get(card_id)

        if not card:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Card ({card_id}) not found"
            )

        if card.list_id != lst.id:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Card ({card_id}) not found"
            )
            # raise HTTPException(
            #     status_code=HTTP_400_BAD_REQUEST,
            #     detail=f"Card ({card.id}) does not connected to List ({lst.id})"
            # )

        return card

    async def create_new_card(self, *, card: card_schema.CardCreate, list_id: int, user_id: int):
        now = datetime.datetime.now()

        return await models.Card.create(
            **card.dict(),
            **{
                'list_id': list_id,
                'last_change_by_id': user_id,
                'last_change_at': now,
                'created_at': now
            }
        )

    async def create_new_card_and_write_history(self, *, card: card_schema.CardCreate, list_id: int, user_id: int):
        new_card = await self.create_new_card(
            card=card,
            list_id=list_id,
            user_id=user_id
        )

        await self.write_history(card=new_card, action=enums.CardHistoryActions.create)

        return new_card

    async def get_list_cards(self, *, list_id: int, offset=0, limit=25):
        if not limit:
            limit = 25

        async with db.transaction():
            cursor = await models.Card.query.where(models.Card.list_id == list_id).gino.iterate()
            if offset:
                await cursor.forward(offset)
            cards = await cursor.many(limit)
        return cards

    async def update(self, *, card: models.Card, updated_card: card_schema.CardUpdate):
        updated_card = updated_card.dict()

        if 'list_id' in updated_card and updated_card.get('list_id'):
            # Import list_repo and board_repo or use queries?
            old_list = await models.List.get(card.list_id)
            board = await models.Board.get(old_list.board_id)

            new_list = await models.List.get(updated_card.get('list_id'))

            if not new_list or new_list.board_id != board.id:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f"List ({updated_card.get('list_id')}) not exists"
                )
        else:
            del updated_card['list_id']

        await card.update(
            **updated_card |
            {'last_change_at': datetime.datetime.now()}
        ).apply()

    async def update_and_write_history(self, *, card: models.Card, updated_card: card_schema.CardUpdate):
        await self.update(card=card, updated_card=updated_card)

        updated_card = updated_card.dict()
        if 'list_id' in updated_card and updated_card.get('list_id'):
            action = enums.CardHistoryActions.move

        await self.write_history(card=card, action=enums.CardHistoryActions.update)

    async def write_history(self, *, card: models.Card, action: enums.CardHistoryActions):
        # Merge card with new fields, rewrite last_change_at field (used python3.9 syntax **{d1 | d1})
        history_data = card_schema.CardHistory(
            **card.to_dict() |
            {
                'card_id': card.to_dict().get('id'),
                'action': action
            }
        )

        await models.CardHistory.create(**history_data.dict())

    async def get_history(self, *, card_id: int, offset=0, limit=25):
        if not limit:
            limit = 25

        async with db.transaction():
            cursor = await models.CardHistory.query.where(models.CardHistory.card_id == card_id).order_by(models.CardHistory.last_change_at.desc()).gino.iterate()
            if offset:
                await cursor.forward(offset)
            history_records = await cursor.many(limit)

        return history_records

    async def delete_by_id(self, *, card_id):
        return await models.Card.delete.returning().where(models.Card.id == card_id).gino.first()

    async def delete_instance(self, *, card: models.Card):
        await card.delete()

        return card

    async def delete_and_write_history(self, *, card: models.Card):
        await card.delete()

        await self.write_history(card=card, action=enums.CardHistoryActions.delete)

        card.last_change_at = datetime.datetime.now()

        return card


card_repo = CardsRepository()
