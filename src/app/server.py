from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core import config
from app.db.database import db


def get_application():
    app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)

    db.init_app(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.include_router(api_router, prefix=config.API_PREFIX)

    return app


app = get_application()
