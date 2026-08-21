import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_health_check():
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.get("/health")
            assert res.status_code == 200


@pytest.mark.asyncio
async def test_rate_limiting():
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            user_id = "test_rate_limit_user"

            for i in range(3):
                res = await client.post(
                    "/documents",
                    json={
                        "user_id": user_id,
                        "title": f"Doc {i}",
                        "content": f"Unique test content body {i}",
                    },
                )
                assert res.status_code == 201