import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.controllers import document, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB and target your document_insights DB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    app.mongodb_client = AsyncIOMotorClient(mongo_uri)
    app.db = app.mongodb_client["document_insights"]
    yield
    app.mongodb_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(document.router)