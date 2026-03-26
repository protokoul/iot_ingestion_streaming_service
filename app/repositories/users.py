from typing import Any

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError


class UserRepository:
    def __init__(self, db: AsyncDatabase) -> None:
        self._collection = db.users

    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        document = payload.copy()
        try:
            await self._collection.insert_one(document)
        except DuplicateKeyError as exc:
            raise ValueError("user_id already exists") from exc

        document.pop("_id", None)
        return document

    async def update(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        await self._collection.update_one({"user_id": user_id}, {"$set": payload})
        return await self.get(user_id)

    async def get(self, user_id: str) -> dict[str, Any] | None:
        return await self._collection.find_one({"user_id": user_id}, {"_id": 0})
