from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_username, get_user_service
from app.schemas.user import ManagedUserCreate, ManagedUserResponse, ManagedUserUpdate
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_current_username)])


@router.post("", response_model=ManagedUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: ManagedUserCreate, service: UserService = Depends(get_user_service)) -> ManagedUserResponse:
    return ManagedUserResponse(**await service.create(payload.model_dump()))


@router.put("/{user_id}", response_model=ManagedUserResponse, status_code=status.HTTP_200_OK)
async def update_user(user_id: str, payload: ManagedUserUpdate, service: UserService = Depends(get_user_service)) -> ManagedUserResponse:
    return ManagedUserResponse(**await service.update(user_id, payload.model_dump()))


@router.get("/{user_id}", response_model=ManagedUserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)) -> ManagedUserResponse:
    return ManagedUserResponse(**await service.get(user_id))
