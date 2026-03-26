from fastapi import Depends, HTTPException, Request, WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import Settings, get_settings
from app.core.security import TokenValidationError, decode_access_token
from app.repositories.accounts import AccountRepository
from app.repositories.iot import IoTRepository
from app.repositories.users import UserRepository
from app.services.auth import AuthService
from app.services.iot import IoTService
from app.services.users import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_db(request: Request) -> AsyncDatabase:
    return request.app.state.mongo_db


def get_settings_dep() -> Settings:
    return get_settings()


def get_account_repo(db: AsyncDatabase = Depends(get_db)) -> AccountRepository:
    return AccountRepository(db)


def get_user_repo(db: AsyncDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_iot_repo(db: AsyncDatabase = Depends(get_db)) -> IoTRepository:
    return IoTRepository(db)


def get_auth_service(
    repo: AccountRepository = Depends(get_account_repo),
    settings: Settings = Depends(get_settings_dep),
) -> AuthService:
    return AuthService(repo, settings)


def get_user_service(repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(repo)


def get_iot_service(
    request: Request,
    iot_repo: IoTRepository = Depends(get_iot_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> IoTService:
    return IoTService(iot_repo=iot_repo, user_repo=user_repo, broadcaster=request.app.state.broadcaster)


async def get_current_username(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings_dep),
) -> str:
    if credentials is None:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization Header",
                )
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                )

    try:
        payload = decode_access_token(credentials.credentials, settings)
    except TokenValidationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return str(payload["sub"])


def get_ws_token(websocket: WebSocket) -> str | None:
    query_token = websocket.query_params.get("token")
    if query_token:
        return query_token
    authorization = websocket.headers.get("authorization")
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token
