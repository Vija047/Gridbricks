import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.services.store import Store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    store = Store()
    ok = store.ensure_db()
    if ok:
        logger.info("Database ready at %s", store.db_path)
    else:
        logger.warning(
            "Database empty — run scripts/sync_january_2026.py or provide seed data"
        )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="UK Wind Forecast Decision Portal API",
        description=(
            "Day-ahead wind forecast vs actuals for UK national wind (Elexon), "
            "January 2026 pilot."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )
    # Demo: allow configured origins plus wildcard for Vercel previews
    origins = settings.cors_origin_list
    if "*" not in origins:
        origins = list(origins) + ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()
