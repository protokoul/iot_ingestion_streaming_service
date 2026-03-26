from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.deps import get_ws_token
from app.core.config import get_settings
from app.core.security import TokenValidationError, decode_access_token
from app.schemas.iot import EventEnvelope, IoTDataIn, IoTDataOut

router = APIRouter(tags=["websockets"])


@router.websocket("/ws/subscribe")
async def subscribe_ws(websocket: WebSocket) -> None:
    settings = get_settings()
    token = get_ws_token(websocket)
    user_id = websocket.query_params.get("user_id")
    if not token or not user_id:
        await websocket.close(code=1008, reason="Missing token or user_id")
        return

    try:
        payload = decode_access_token(token, settings)
    except TokenValidationError as exc:
        await websocket.close(code=1008, reason=str(exc))
        return

    exp = payload.get("exp")
    manager = websocket.app.state.connection_manager
    await manager.subscribe(user_id=user_id, websocket=websocket, disconnect_at_epoch=int(exp) if exp else None)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.unsubscribe(websocket)


@router.websocket("/ws/ingest")
async def ingest_ws(websocket: WebSocket) -> None:
    settings = get_settings()
    token = get_ws_token(websocket)
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    try:
        payload = decode_access_token(token, settings)
    except TokenValidationError as exc:
        await websocket.close(code=1008, reason=str(exc))
        return

    exp = payload.get("exp")
    manager = websocket.app.state.connection_manager
    service = websocket.app.state.iot_service_factory()
    await manager.register_ingest_socket(websocket=websocket, disconnect_at_epoch=int(exp) if exp else None)

    try:
        while True:
            message = await websocket.receive_json()
            dto = IoTDataIn.model_validate(message)
            saved = await service.ingest(dto.model_dump())
            envelope = EventEnvelope(event="INGESTED", data=IoTDataOut(**saved))
            await websocket.send_json(envelope.model_dump())
    except WebSocketDisconnect:
        await manager.unsubscribe(websocket)
    except Exception as exc:
        await websocket.send_json({"event": "ERROR", "detail": str(exc)})
