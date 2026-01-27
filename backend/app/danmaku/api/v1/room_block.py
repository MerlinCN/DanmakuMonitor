from fastapi import APIRouter
from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import InstrumentedAttribute

from backend.app.danmaku.model.live import RoomBlockMsg
from backend.app.danmaku.schema.danmaku import (
    GetRoomBlockDetail,
    RoomBlockCountFilters,
    RoomBlockSearchFilters,
    RoomBlockSortField,
    SortOrder,
)
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()

ROOM_BLOCK_SORT_FIELD_MAP: dict[RoomBlockSortField, InstrumentedAttribute] = {
    RoomBlockSortField.TIMESTAMP: RoomBlockMsg.timestamp,
}


def _apply_time_filter(stmt: Select, filters: RoomBlockSearchFilters) -> Select:
    if filters.start_date and filters.end_date:
        return stmt.where(RoomBlockMsg.timestamp.between(filters.start_date, filters.end_date))
    if filters.start_date:
        return stmt.where(RoomBlockMsg.timestamp >= filters.start_date)
    if filters.end_date:
        return stmt.where(RoomBlockMsg.timestamp <= filters.end_date)
    return stmt


def _apply_room_block_filters(stmt: Select, filters: RoomBlockSearchFilters) -> Select:
    stmt = _apply_time_filter(stmt, filters)
    if filters.user_mid:
        stmt = stmt.where(RoomBlockMsg.user_mid == filters.user_mid)
    if filters.user_name:
        stmt = stmt.where(RoomBlockMsg.user_name.ilike(f'%{filters.user_name}%'))
    if filters.room_id:
        stmt = stmt.where(RoomBlockMsg.room_id == filters.room_id)
    return stmt


@router.post('/search', dependencies=[DependsPagination])
async def search_room_block(
    db: CurrentSession,
    filters: RoomBlockSearchFilters,
) -> ResponseSchemaModel[PageData[GetRoomBlockDetail]]:
    stmt = _apply_room_block_filters(select(RoomBlockMsg), filters)

    sort_column = (
        ROOM_BLOCK_SORT_FIELD_MAP.get(filters.sort_by, RoomBlockMsg.timestamp)
        if filters.sort_by
        else RoomBlockMsg.timestamp
    )
    sort_func = asc if filters.sort_order == SortOrder.ASC else desc
    stmt = stmt.order_by(sort_func(sort_column))

    page_data = await paging_data(db, stmt)
    return response_base.success(data=page_data)


@router.post('/count')
async def count_room_block(
    db: CurrentSession,
    filters: RoomBlockCountFilters,
) -> ResponseSchemaModel[int]:
    stmt = select(func.count()).select_from(RoomBlockMsg)
    if filters.user_mid:
        stmt = stmt.where(RoomBlockMsg.user_mid == filters.user_mid)
    if filters.room_id:
        stmt = stmt.where(RoomBlockMsg.room_id == filters.room_id)
    result = await db.execute(stmt)
    count = result.scalar() or 0
    return response_base.success(data=count)
