from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.admin.deps import ensure_default_admin
from app.api.v1.router import api_router
from app.db.session import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时确保默认管理员存在(账号 admin,密码来自 .env ADMIN_INIT_PASSWORD)
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Arya_handcraft API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 开发期全放行;生产环境收敛为 H5/后台域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
