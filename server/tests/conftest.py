"""pytest 全局配置:用 SQLite 内存库 + 依赖覆盖,避免依赖本地 PostgreSQL/Redis/微信。"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import ratelimit
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401  确保模型注册


# SQLite 只有 INTEGER PRIMARY KEY 才自增;让 BigInteger 主键在 SQLite 下编译为 INTEGER
@compiles(BigInteger, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):
    return "INTEGER"


TEST_SQLALCHEMY_URL = "sqlite://"


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    """每个测试独立限流窗口,避免进程级计数跨测试污染。"""
    ratelimit.reset()
    yield
    ratelimit.reset()


@pytest.fixture()
def db_session():
    engine = create_engine(
        TEST_SQLALCHEMY_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal
    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    return TestClient(fastapi_app)