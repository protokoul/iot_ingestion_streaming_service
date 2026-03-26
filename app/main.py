import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.iot import router as iot_router
from app.api.routes.users import router as users_router
from app.api.routes.ws import router as ws_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.mongo import create_mongo_client, ensure_indexes
from app.db.redis import create_redis_client
from app.repositories.iot import IoTRepository
from app.repositories.users import UserRepository
from app.repositories.accounts import AccountRepository
from app.services.auth import AuthService
from app.services.iot import IoTService
from app.services.realtime import ConnectionManager, RedisBroadcaster

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    mongo_client = await create_mongo_client(settings)
    await ensure_indexes(mongo_client, settings.mongo_db_name)
    mongo_db = mongo_client[settings.mongo_db_name]

    redis_client = await create_redis_client(settings)
    connection_manager = ConnectionManager()
    broadcaster = RedisBroadcaster(redis_client, settings.redis_channel_prefix, connection_manager)

    app.state.mongo_client = mongo_client
    app.state.mongo_db = mongo_db
    app.state.redis = redis_client
    app.state.connection_manager = connection_manager
    app.state.broadcaster = broadcaster

    auth_service = AuthService(AccountRepository(mongo_db), settings)
    await auth_service.bootstrap_admin()

    def iot_service_factory() -> IoTService:
        return IoTService(
            iot_repo=IoTRepository(mongo_db),
            user_repo=UserRepository(mongo_db),
            broadcaster=broadcaster,
        )

    app.state.iot_service_factory = iot_service_factory

    await broadcaster.start()
    logger.info("Application startup complete")
    try:
        yield
    finally:
        await broadcaster.stop()
        await redis_client.aclose()
        mongo_client.close()
        logger.info("Application shutdown complete")


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def healthcheck() -> JSONResponse:
    return JSONResponse(content={"status": "ok"}, status_code=200)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(iot_router)
app.include_router(ws_router)
