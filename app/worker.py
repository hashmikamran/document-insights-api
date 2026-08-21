import asyncio
import random
import logging
from datetime import datetime
from app.database import db, redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("doc_worker")

async def process_job(doc):
    doc_id = doc["_id"]
    user_id = doc["user_id"]

    await db.documents.update_one(
        {"_id": doc_id},
        {"$set": {"status": "processing", "updated_at": datetime.utcnow()}}
    )
    logger.info(f"Processing doc {doc_id} for user {user_id}")

    await asyncio.sleep(random.randint(10, 30))

    if random.random() < 0.10:
        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {"status": "failed", "error": "Processing failed", "updated_at": datetime.utcnow()}}
        )
        logger.error(f"Doc {doc_id} failed")
    else:
        word_count = len(doc["content"].split())
        summary = f"Summary: Document contains {word_count} words discussing '{doc['title']}'."
        
        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {"status": "completed", "summary": summary, "updated_at": datetime.utcnow()}}
        )
        redis_client.setex(f"cache:{doc['content_hash']}", 86400, summary)
        logger.info(f"Doc {doc_id} completed")

    current_jobs = int(redis_client.get(f"active_jobs:{user_id}") or 0)
    if current_jobs > 0:
        redis_client.decr(f"active_jobs:{user_id}")

async def start_worker():
    logger.info("Worker started")
    while True:
        try:
            doc = await db.documents.find_one({"status": "queued"})
            if doc:
                await process_job(doc)
            else:
                await asyncio.sleep(2)
        except Exception as err:
            logger.error(f"Worker loop exception: {err}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(start_worker())