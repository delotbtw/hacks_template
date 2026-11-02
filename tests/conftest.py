from collections.abc import AsyncIterator

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.db import get_session
from app.core.redis import redis_client
from app.main import app
from app.models import Base

TEST_DB = f"{get_settings().postgres_db}_test"


def _url(db: str) -> str:
    s = get_settings()
    return f"postgresql+asyncpg://{s.postgres_user}:{s.postgres_password}@{s.postgres_host}:{s.postgres_port}/{db}"


async def recreate_database(name: str) -> None:
    """Создаёт пустую БД (удаляя старую) через служебную БД postgres."""
    s = get_settings()
    conn = await asyncpg.connect(
        user=s.postgres_user,
        password=s.postgres_password,
        host=s.postgres_host,
        port=s.postgres_port,
        database="postgres",
    )
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        await conn.execute(f'CREATE DATABASE "{name}"')
    finally:
        await conn.close()


@pytest.fixture(scope="session")
def db_url_factory():
    return _url


@pytest_asyncio.fixture(scope="session")
async def engine():
    await recreate_database(TEST_DB)
    eng = create_async_engine(_url(TEST_DB), poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
    """Сессия в транзакции, которая откатывается после теста (commit в коде = savepoint)."""
    async with engine.connect() as conn:
        trans = await conn.begin()
        sess = AsyncSession(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        yield sess
        await sess.close()
        await trans.rollback()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def clean_redis() -> AsyncIterator[None]:
    await redis_client.flushdb()
    yield
    await redis_client.flushdb()
