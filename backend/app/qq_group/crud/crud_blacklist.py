import uuid

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.qq_group.model import Blacklist


class CRUDBlacklist(CRUDPlus[Blacklist]):
    async def get(self, db: AsyncSession, pk: uuid.UUID) -> Blacklist | None:
        return await self.select_model(db, pk)

    async def get_all(self, db: AsyncSession) -> Sequence[Blacklist]:
        return await self.select_models(db)

    async def get_by_bilibili_uid(self, db: AsyncSession, bilibili_uid: int) -> Blacklist | None:
        return await self.select_model_by_column(db, bilibili_uid=bilibili_uid)

    async def get_by_qq_uid(self, db: AsyncSession, qq_uid: int) -> Blacklist | None:
        return await self.select_model_by_column(db, qq_uid=qq_uid)

    async def is_blocked(self, db: AsyncSession, *, bilibili_uid: int | None = None, qq_uid: int | None = None) -> bool:
        if bilibili_uid:
            result = await self.get_by_bilibili_uid(db, bilibili_uid)
            if result:
                return True
        if qq_uid:
            result = await self.get_by_qq_uid(db, qq_uid)
            if result:
                return True
        return False

    async def create(self, db: AsyncSession, *, bilibili_uid: int | None = None, qq_uid: int | None = None) -> None:
        obj = Blacklist(bilibili_uid=bilibili_uid, qq_uid=qq_uid)
        db.add(obj)

    async def delete(self, db: AsyncSession, pk: uuid.UUID) -> int:
        return await self.delete_model(db, pk)

    async def delete_by_bilibili_uid(self, db: AsyncSession, bilibili_uid: int) -> int:
        return await self.delete_model_by_column(db, bilibili_uid=bilibili_uid)

    async def delete_by_qq_uid(self, db: AsyncSession, qq_uid: int) -> int:
        return await self.delete_model_by_column(db, qq_uid=qq_uid)


blacklist_dao: CRUDBlacklist = CRUDBlacklist(Blacklist)
