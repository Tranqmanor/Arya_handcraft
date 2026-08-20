# 本目录说明

`server/` 为 FastAPI 后端,结构见 preplan.md 第 4.2 节。

## 开发环境(固定)

- 使用 **miniconda 的 `fastapi` 环境**:`F:\miniconda3\envs\fastapi\python.exe`(Python 3.12.13)
- 后续所有 Python 命令均使用该环境执行;如需在终端手动运行:

```powershell
& F:\miniconda3\envs\fastapi\python.exe -m pip install -r requirements.txt
& F:\miniconda3\envs\fastapi\python.exe -m uvicorn app.main:app --reload
```

## 本地启动

```bash
cd server
cp .env.example .env     # 首次;.env 已存在则跳过
docker compose up -d db redis     # 先起数据库与 Redis(需已安装 Docker)
pip install -r requirements.txt   # 或使用 fastapi 环境的 python
alembic upgrade head              # 建表
uvicorn app.main:app --reload     # 启动 API,访问 http://localhost:8000/docs
```

> 当前环境已确认安装了 fastapi/sqlalchemy/pydantic/alembic/uvicorn/psycopg/pydantic_settings/httpx/redis 与 python-jose。

## JWT_SECRET 生成

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 测试

```bash
pytest
```
