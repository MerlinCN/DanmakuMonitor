from typing import Any

import httpx

from fastapi import APIRouter, Request, Response

from backend.core.conf import settings

router = APIRouter()


def _build_upstream_url(path: str) -> str:
    """构建上游服务 URL"""
    base = f'http://{settings.QQ_GROUP_API_HOST}:{settings.QQ_GROUP_API_PORT}'
    return f'{base}/api/v1/qq-group{path}'


@router.api_route('/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
async def proxy_request(request: Request, path: str) -> Response:
    """
    转发请求到 QQ 群验证服务

    :param request: FastAPI 请求对象
    :param path: 请求路径
    :return: 上游服务响应
    """
    upstream_url = _build_upstream_url(f'/{path}' if path else '')

    headers = dict(request.headers)
    headers.pop('host', None)

    body: bytes | None = None
    if request.method in ('POST', 'PUT', 'PATCH'):
        body = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream_response = await client.request(
            method=request.method,
            url=upstream_url,
            headers=headers,
            params=request.query_params,
            content=body,
        )

    response_headers: dict[str, Any] = dict(upstream_response.headers)
    response_headers.pop('content-encoding', None)
    response_headers.pop('content-length', None)
    response_headers.pop('transfer-encoding', None)

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get('content-type'),
    )
