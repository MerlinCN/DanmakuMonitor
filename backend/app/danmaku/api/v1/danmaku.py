from fastapi import APIRouter
from sqlalchemy import Select, asc, desc, select
from sqlalchemy.orm import InstrumentedAttribute

from backend.app.danmaku.model.live import DanmakuMessage, GuardLevel
from backend.app.danmaku.schema.danmaku import DanmakuSearchFilters, DanmakuSortField, GetDanmakuDetail, SortOrder
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()

DANMAKU_SORT_FIELD_MAP: dict[DanmakuSortField, InstrumentedAttribute] = {
    DanmakuSortField.TIMESTAMP: DanmakuMessage.timestamp,
    DanmakuSortField.FANS_MEDAL_LEVEL: DanmakuMessage.fans_medal_level,
    DanmakuSortField.GUARD_LEVEL: DanmakuMessage.guard_level,
}


def _apply_time_filter(stmt: Select, filters: DanmakuSearchFilters) -> Select:
    if filters.start_date and filters.end_date:
        return stmt.where(DanmakuMessage.timestamp.between(filters.start_date, filters.end_date))
    if filters.start_date:
        return stmt.where(DanmakuMessage.timestamp >= filters.start_date)
    if filters.end_date:
        return stmt.where(DanmakuMessage.timestamp <= filters.end_date)
    return stmt


def _apply_danmaku_filters(stmt: Select, filters: DanmakuSearchFilters) -> Select:
    stmt = _apply_time_filter(stmt, filters)
    if filters.user_mid:
        stmt = stmt.where(DanmakuMessage.user_mid == filters.user_mid)
    if filters.user_name:
        stmt = stmt.where(DanmakuMessage.user_name.ilike(f'%{filters.user_name}%'))
    if filters.message:
        stmt = stmt.where(DanmakuMessage.message.ilike(f'%{filters.message}%'))
    if filters.room_id:
        stmt = stmt.where(DanmakuMessage.room_id == filters.room_id)
    if filters.fans_medal_name:
        stmt = stmt.where(DanmakuMessage.fans_medal_name.ilike(f'%{filters.fans_medal_name}%'))
    if filters.guard_level is not None:
        stmt = stmt.where(DanmakuMessage.guard_level == GuardLevel(filters.guard_level))
    if filters.fans_medal_level is not None:
        stmt = stmt.where(DanmakuMessage.fans_medal_level >= filters.fans_medal_level)
    return stmt


@router.post('/search', dependencies=[DependsPagination])
async def search_danmaku(
    db: CurrentSession,
    filters: DanmakuSearchFilters,
) -> ResponseSchemaModel[PageData[GetDanmakuDetail]]:
    stmt = _apply_danmaku_filters(select(DanmakuMessage), filters)

    sort_column = (
        DANMAKU_SORT_FIELD_MAP.get(filters.sort_by, DanmakuMessage.timestamp)
        if filters.sort_by
        else DanmakuMessage.timestamp
    )
    sort_func = asc if filters.sort_order == SortOrder.ASC else desc
    stmt = stmt.order_by(sort_func(sort_column))

    page_data = await paging_data(db, stmt)
    return response_base.success(data=page_data)
