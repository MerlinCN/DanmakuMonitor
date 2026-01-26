from fastapi import APIRouter
from sqlalchemy import Select, asc, desc, select
from sqlalchemy.orm import InstrumentedAttribute

from backend.app.danmaku.model.live import SuperChatMessage
from backend.app.danmaku.schema.danmaku import GetSuperchatDetail, SortOrder, SuperchatSearchFilters, SuperchatSortField
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()

SUPERCHAT_SORT_FIELD_MAP: dict[SuperchatSortField, InstrumentedAttribute] = {
    SuperchatSortField.TIMESTAMP: SuperChatMessage.timestamp,
    SuperchatSortField.FANS_MEDAL_LEVEL: SuperChatMessage.fans_medal_level,
    SuperchatSortField.GUARD_LEVEL: SuperChatMessage.guard_level,
    SuperchatSortField.PRICE: SuperChatMessage.price,
}


def _apply_time_filter(stmt: Select, filters: SuperchatSearchFilters) -> Select:
    if filters.start_date and filters.end_date:
        return stmt.where(SuperChatMessage.timestamp.between(filters.start_date, filters.end_date))
    if filters.start_date:
        return stmt.where(SuperChatMessage.timestamp >= filters.start_date)
    if filters.end_date:
        return stmt.where(SuperChatMessage.timestamp <= filters.end_date)
    return stmt


def _apply_superchat_filters(stmt: Select, filters: SuperchatSearchFilters) -> Select:
    stmt = _apply_time_filter(stmt, filters)
    if filters.user_mid:
        stmt = stmt.where(SuperChatMessage.user_mid == filters.user_mid)
    if filters.user_name:
        stmt = stmt.where(SuperChatMessage.user_name.ilike(f'%{filters.user_name}%'))
    if filters.message:
        stmt = stmt.where(SuperChatMessage.message.ilike(f'%{filters.message}%'))
    if filters.room_id:
        stmt = stmt.where(SuperChatMessage.room_id == filters.room_id)
    return stmt


@router.post('', dependencies=[DependsPagination])
async def search_superchat(
    db: CurrentSession,
    filters: SuperchatSearchFilters,
) -> ResponseSchemaModel[PageData[GetSuperchatDetail]]:
    stmt = _apply_superchat_filters(select(SuperChatMessage), filters)

    sort_column = (
        SUPERCHAT_SORT_FIELD_MAP.get(filters.sort_by, SuperChatMessage.timestamp)
        if filters.sort_by
        else SuperChatMessage.timestamp
    )
    sort_func = asc if filters.sort_order == SortOrder.ASC else desc
    stmt = stmt.order_by(sort_func(sort_column))

    page_data = await paging_data(db, stmt)
    return response_base.success(data=page_data)
