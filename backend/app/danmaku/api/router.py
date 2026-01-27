from fastapi import APIRouter

from backend.app.danmaku.api.v1.danmaku import router as danmaku_router
from backend.app.danmaku.api.v1.room_block import router as room_block_router
from backend.app.danmaku.api.v1.superchat import router as superchat_router
from backend.core.conf import settings

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

v1.include_router(danmaku_router, prefix='/danmaku', tags=['弹幕查询'])
v1.include_router(superchat_router, prefix='/superchat', tags=['醒目留言查询'])
v1.include_router(room_block_router, prefix='/room-block', tags=['房间禁言查询'])
