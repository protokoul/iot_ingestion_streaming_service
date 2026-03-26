from pymongo import ASCENDING, DESCENDING, AsyncMongoClient

from app.core.config import Settings


async def create_mongo_client(settings: Settings) -> AsyncMongoClient:
    client = AsyncMongoClient(settings.mongo_uri)
    return client


async def ensure_indexes(client: AsyncMongoClient, db_name: str) -> None:
    db = client[db_name]
    await db.accounts.create_index([("username", ASCENDING)], unique=True, name="uq_accounts_username")
    await db.users.create_index([("user_id", ASCENDING)], unique=True, name="uq_users_user_id")
    await db.iot_data.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)], name="idx_iot_user_ts")
