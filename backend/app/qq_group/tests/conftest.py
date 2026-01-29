from collections.abc import AsyncGenerator

import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.db import qq_group_async_db_session


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession]:
    async with qq_group_async_db_session() as session:
        yield session
