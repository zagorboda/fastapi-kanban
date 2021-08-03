from fastapi import APIRouter
from app.api.routes.users import router as user_router
from app.api.routes.boards import router as board_router
from app.api.routes.lists import router as list_router

router = APIRouter()
router.include_router(user_router)
router.include_router(board_router)
router.include_router(list_router)
