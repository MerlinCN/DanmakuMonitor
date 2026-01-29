from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.qq_group.model import Cookies


class CRUDCookies(CRUDPlus[Cookies]):
    async def get(self, db: AsyncSession) -> Cookies | None:
        stmt = select(Cookies).where(Cookies.id == 1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        db: AsyncSession,
        *,
        sessdata: str | None = None,
        bili_jct: str | None = None,
        buvid3: str | None = None,
        buvid4: str | None = None,
        dedeuserid: str | None = None,
        ac_time_value: str | None = None,
    ) -> None:
        existing = await self.get(db)
        if existing:
            if sessdata is not None:
                existing.sessdata = sessdata
            if bili_jct is not None:
                existing.bili_jct = bili_jct
            if buvid3 is not None:
                existing.buvid3 = buvid3
            if buvid4 is not None:
                existing.buvid4 = buvid4
            if dedeuserid is not None:
                existing.dedeuserid = dedeuserid
            if ac_time_value is not None:
                existing.ac_time_value = ac_time_value
        else:
            obj = Cookies(
                sessdata=sessdata,
                bili_jct=bili_jct,
                buvid3=buvid3,
                buvid4=buvid4,
                dedeuserid=dedeuserid,
                ac_time_value=ac_time_value,
            )
            db.add(obj)


cookies_dao: CRUDCookies = CRUDCookies(Cookies)
