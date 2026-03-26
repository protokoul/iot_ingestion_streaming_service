from typing import Any

from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase


class IoTRepository:
    def __init__(self, db: AsyncDatabase) -> None:
        self._collection = db.iot_data

    async def insert(self, payload: dict[str, Any]) -> dict[str, Any]:
        document = payload.copy()
        await self._collection.insert_one(document)
        document.pop("_id", None)
        return document

    async def get_latest(self, user_id: str) -> dict[str, Any] | None:
        return await self._collection.find_one(
            {"user_id": user_id},
            {"_id": 0},
            sort=[("timestamp", DESCENDING)],
        )

    async def get_history(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        cursor = self._collection.find({"user_id": user_id}, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit)
        return await cursor.to_list(length=limit)
