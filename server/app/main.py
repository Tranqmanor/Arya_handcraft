from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.admin.deps import ensure_default_admin
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import SessionLocal

logger = logging.getLogger("arya")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时确保默认管理员存在(账号 admin,密码来自 .env ADMIN_INIT_PASSWORD)。
    # 失败不阻塞进程启动:数据库暂不可达/迁移未完成时,应用仍可启动,
    # 便于通过 /docs 与日志排查;数据库就绪后重启即可完成初始化。
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    except Exception as exc:  # noqa: BLE001
        logger.warning("ensure_default_admin failed (DB not ready?): %s", exc)
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

# CORS:配置了 CORS_ORIGINS 白名单则严格收敛;
# 未配置时仅开发环境(ENV=dev)放行所有,生产环境不放开任何跨域来源
_settings = get_settings()
if _settings.cors_origin_list:
    _allow_origins = _settings.cors_origin_list
elif _settings.ENV == "dev":
    _allow_origins = ["*"]
else:
    _allow_origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
