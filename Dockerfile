FROM python:3.11.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 设置工作目录
WORKDIR /app


COPY . .

RUN useradd -m -u 1000 appuser

# 同步 uv 配置
RUN uv sync --index-url https://mirrors.aliyun.com/pypi/simple

# USER appuser
# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "-m","uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
