from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.danmaku.model import Credential

SINGLETON_ID = 1


class CRUDCredential(CRUDPlus[Credential]):
    async def get(self, db: AsyncSession) -> Credential | None:
        return await self.select_model(db, SINGLETON_ID)

    async def exists(self, db: AsyncSession) -> bool:
        return await self.select_model(db, SINGLETON_ID) is not None

    async def upsert(
        self,
        db: AsyncSession,
        *,
        sessdata: str,
        bili_jct: str,
        buvid3: str | None = None,
        buvid4: str | None = None,
        dedeuserid: str | None = None,
        ac_time_value: str | None = None,
    ) -> Credential:
        existing = await self.get(db)
        data = {
            'sessdata': sessdata,
            'bili_jct': bili_jct,
            'buvid3': buvid3,
            'buvid4': buvid4,
            'dedeuserid': dedeuserid,
            'ac_time_value': ac_time_value,
        }

        if existing:
            await self.update_model(db, SINGLETON_ID, data)
            await db.refresh(existing)
            return existing

        new_credential = Credential(**data)
        db.add(new_credential)
        await db.flush()
        return new_credential

    async def delete(self, db: AsyncSession) -> int:
        return await self.delete_model(db, SINGLETON_ID)


credential_dao: CRUDCredential = CRUDCredential(Credential)
