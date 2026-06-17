import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from booking_service.api.limiter import limiter
from booking_service.db import Base, get_session
from booking_service.main import app


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session, monkeypatch):
    app.dependency_overrides[get_session] = lambda: session
    monkeypatch.setattr(
        "booking_service.logic.booking.confirm_booking.delay",
        lambda *a, **k: None,
    )
    limiter.enabled = False
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
    ) as c:
        yield c
    app.dependency_overrides.clear()
