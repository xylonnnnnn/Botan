import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from .models import Base

DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")


def get_engine(db_url: Optional[str] = None) -> AsyncEngine:
    url = db_url or DATABASE_URL
    return create_async_engine(url, echo=False, future=True)


_engine: Optional[AsyncEngine] = None
_SessionFactory: Optional[async_sessionmaker[AsyncSession]] = None


def setup(db_url: Optional[str] = None) -> None:
    global _engine, _SessionFactory
    _engine = get_engine(db_url)
    _SessionFactory = async_sessionmaker(_engine, expire_on_commit=False)


def session_factory() -> async_sessionmaker[AsyncSession]:
    if _SessionFactory is None:
        setup()
    assert _SessionFactory is not None
    return _SessionFactory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    sf = session_factory()
    async with sf() as session:
        yield session


async def init_db(db_url: Optional[str] = None) -> None:
    if _engine is None:
        setup(db_url)

    assert _engine is not None
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory()() as session:
        await session.execute(text("SELECT 1"))