from fastapi import APIRouter

from backend.app.qq_group.api.v1.proxy import router as proxy_router
from backend.core.conf import settings

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

v1.include_router(proxy_router, prefix='/qq-group', tags=['QQ群验证'])
