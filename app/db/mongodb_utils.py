from motor.motor_asyncio import AsyncIOMotorClient

from app.db.mongodb import db
from app.settings import settings


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(
        settings.mongo_url(),
        maxPoolSize=settings.mongo_max_connections_count,
        minPoolSize=settings.mongo_min_connections_count,
    )


async def close_mongo_connection():
    db.client.close()
