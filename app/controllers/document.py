import hashlib
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Request, status

from app.config import settings
from app.database import redis_client  # Synchronous Redis instance
from app.models.document import DocumentSubmit

router = APIRouter(tags=["Documents"])


def get_content_hash(text: str) -> str:
    """Generate SHA-256 hash for document content to handle caching."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@router.post("/documents", status_code=status.HTTP_201_CREATED)
async def submit_document(request: Request, payload: DocumentSubmit):
    """Submit a document. Checks Redis cache first, applies rate-limiting, and queues document."""
    # Use request.app.db to bind Motor queries to active event loop
    db = request.app.db
    content_hash = get_content_hash(payload.content)

    # 1. Check Redis Cache for pre-computed summary
    cached_summary = redis_client.get(f"cache:{content_hash}")
    if cached_summary:
        # Decode byte string if Redis client returns bytes
        if isinstance(cached_summary, bytes):
            cached_summary = cached_summary.decode("utf-8")

        doc_data = {
            "user_id": payload.user_id,
            "title": payload.title,
            "content": payload.content,
            "content_hash": content_hash,
            "status": "completed",
            "summary": cached_summary,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = await db.documents.insert_one(doc_data)
        return {
            "document_id": str(res.inserted_id),
            "status": "completed",
            "summary": cached_summary,
        }

    # 2. Rate Limiting: Check active jobs for this user
    active_jobs = int(redis_client.get(f"active_jobs:{payload.user_id}") or 0)
    if active_jobs >= settings.MAX_ACTIVE_JOBS_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: Maximum 3 active documents in queue or processing.",
        )

    # 3. Queue new document job
    doc_data = {
        "user_id": payload.user_id,
        "title": payload.title,
        "content": payload.content,
        "content_hash": content_hash,
        "status": "queued",
        "summary": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    res = await db.documents.insert_one(doc_data)
    redis_client.incr(f"active_jobs:{payload.user_id}")

    return {"document_id": str(res.inserted_id), "status": "queued"}


@router.get("/documents/{document_id}")
async def get_document_status(request: Request, document_id: str):
    """Retrieve processing status and summary for a single document."""
    db = request.app.db

    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format",
        )

    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return {
        "document_id": str(doc["_id"]),
        "status": doc["status"],
        "summary": doc.get("summary"),
    }


@router.get("/users/{user_id}/documents")
async def list_user_documents(
    request: Request,
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """Fetch paginated documents belonging to a given user."""
    db = request.app.db
    query = {"user_id": user_id}

    if status_filter:
        query["status"] = status_filter

    skip = (page - 1) * page_size
    cursor = db.documents.find(query).skip(skip).limit(page_size)
    docs = await cursor.to_list(length=page_size)

    results = [
        {
            "document_id": str(d["_id"]),
            "title": d.get("title"),
            "status": d.get("status"),
            "summary": d.get("summary"),
        }
        for d in docs
    ]

    return {
        "page": page,
        "page_size": page_size,
        "documents": results,
    }