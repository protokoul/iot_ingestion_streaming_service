from fastapi import HTTPException, status

from app.repositories.iot import IoTRepository
from app.repositories.users import UserRepository
from app.services.realtime import RedisBroadcaster


class IoTService:
    def __init__(
        self,
        iot_repo: IoTRepository,
        user_repo: UserRepository,
        broadcaster: RedisBroadcaster,
    ) -> None:
        self.iot_repo = iot_repo
        self.user_repo = user_repo
        self.broadcaster = broadcaster

    async def ingest(self, payload: dict) -> dict:
        user = await self.user_repo.get(payload["user_id"])
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user["status"] != "active":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

        saved = await self.iot_repo.insert(payload)
        envelope = {"event": "NEW_DATA", "data": saved}
        await self.broadcaster.publish(payload["user_id"], envelope)
        return saved

    async def latest(self, user_id: str) -> dict:
        latest = await self.iot_repo.get_latest(user_id)
        if not latest:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No IoT data found")
        return latest

    async def history(self, user_id: str, limit: int) -> list[dict]:
        return await self.iot_repo.get_history(user_id, limit)
