import uuid

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.qq_group.model import User


class CRUDUser(CRUDPlus[User]):
    async def get(self, db: AsyncSession, pk: uuid.UUID) -> User | None:
        return await self.select_model(db, pk)

    async def get_all(self, db: AsyncSession) -> Sequence[User]:
        return await self.select_models(db)

    async def get_by_bilibili_uid(self, db: AsyncSession, bilibili_uid: int) -> User | None:
        return await self.select_model_by_column(db, bilibili_uid=bilibili_uid)

    async def get_by_qq_uid(self, db: AsyncSession, qq_uid: int) -> User | None:
        return await self.select_model_by_column(db, qq_uid=qq_uid)

    async def create(self, db: AsyncSession, *, bilibili_uid: int, qq_uid: int) -> None:
        obj = User(bilibili_uid=bilibili_uid, qq_uid=qq_uid)
        db.add(obj)

    async def delete(self, db: AsyncSession, pk: uuid.UUID) -> int:
        return await self.delete_model(db, pk)

    async def delete_by_bilibili_uid(self, db: AsyncSession, bilibili_uid: int) -> int:
        return await self.delete_model_by_column(db, bilibili_uid=bilibili_uid)

    async def delete_by_qq_uid(self, db: AsyncSession, qq_uid: int) -> int:
        return await self.delete_model_by_column(db, qq_uid=qq_uid)


qq_user_dao: CRUDUser = CRUDUser(User)
