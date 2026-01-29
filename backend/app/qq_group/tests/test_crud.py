import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.qq_group.crud import blacklist_dao, cookies_dao, qq_user_dao


@pytest.mark.asyncio
async def test_blacklist_get_all(db: AsyncSession) -> None:
    result = await blacklist_dao.get_all(db)
    assert isinstance(result, (list, tuple))


@pytest.mark.asyncio
async def test_user_get_all(db: AsyncSession) -> None:
    result = await qq_user_dao.get_all(db)
    assert isinstance(result, (list, tuple))


@pytest.mark.asyncio
async def test_cookies_query(db: AsyncSession) -> None:
    result = await cookies_dao.get(db)
    assert result is None or result.id == 1
