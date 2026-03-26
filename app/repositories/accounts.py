from typing import Any

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError


class AccountRepository:
    def __init__(self, db: AsyncDatabase) -> None:
        self._collection = db.accounts

    async def create(self, username: str, hashed_password: str) -> dict[str, Any]:
        document = {"username": username, "hashed_password": hashed_password}
        try:
            await self._collection.insert_one(document)
        except DuplicateKeyError as exc:
            raise ValueError("username already exists") from exc
        return {"username": username, "hashed_password": hashed_password}

    async def get_by_username(self, username: str) -> dict[str, Any] | None:
        return await self._collection.find_one({"username": username}, {"_id": 0})
