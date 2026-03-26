from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_username, get_iot_service
from app.schemas.iot import IoTDataIn, IoTDataOut
from app.services.iot import IoTService

router = APIRouter(tags=["iot"], dependencies=[Depends(get_current_username)])


@router.post("/iot/data", response_model=IoTDataOut, status_code=status.HTTP_201_CREATED)
async def ingest_data(payload: IoTDataIn, service: IoTService = Depends(get_iot_service)) -> IoTDataOut:
    return IoTDataOut(**await service.ingest(payload.model_dump()))


@router.get("/users/{user_id}/iot/latest", response_model=IoTDataOut, status_code=status.HTTP_200_OK)
async def latest_data(user_id: str, service: IoTService = Depends(get_iot_service)) -> IoTDataOut:
    return IoTDataOut(**await service.latest(user_id))


@router.get("/users/{user_id}/iot/history", response_model=list[IoTDataOut], status_code=status.HTTP_200_OK)
async def history_data(
    user_id: str,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    service: IoTService = Depends(get_iot_service),
) -> list[IoTDataOut]:
    history = await service.history(user_id, limit)
    return [IoTDataOut(**item) for item in history]
