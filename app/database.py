import redis
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
db = mongo_client[settings.DATABASE_NAME]

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
    protocol=2
)

async def init_db():
    await db.documents.create_index([("user_id", 1), ("status", 1)])
    
    await db.documents.create_index("content_hash")