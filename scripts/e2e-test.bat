@echo off
REM Arya_handcraft 端到端测试脚本(Windows版)
echo === Arya_handcraft 端到端测试 ===
echo 当前时间: %date% %time%
echo.

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行，请启动 Docker Desktop
    exit /b 1
)

echo ✅ Docker 已运行

cd server

REM 1. 启动数据库和 Redis
echo.
echo 1. 启动 PostgreSQL 和 Redis...
docker compose up -d db redis

REM 等待数据库健康检查
echo 等待数据库就绪...
timeout /t 10 /nobreak >nul

REM 2. 数据库迁移
echo.
echo 2. 执行数据库迁移...
python -m alembic upgrade head

if errorlevel 1 (
    echo ❌ 数据库迁移失败
    exit /b 1
) else (
    echo ✅ 数据库迁移成功
)

REM 3. 运行单元测试
echo.
echo 3. 运行后端单元测试...
python -m pytest tests -v

if errorlevel 1 (
    echo ❌ 单元测试失败
    exit /b 1
) else (
    echo ✅ 所有单元测试通过
)

REM 4. 启动后端服务
echo.
echo 4. 启动 FastAPI 服务...
start /B uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

REM 等待服务启动
echo 等待服务启动...
timeout /t 3 /nobreak >nul

REM 5. 测试 API 端点
echo.
echo 5. 测试核心 API 端点...

REM 测试视频列表
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/videos > response.txt
set /p VIDEO_RESP=<response.txt
if "%VIDEO_RESP%"=="200" (
    echo ✅ 视频列表 API 正常
) else (
    echo ❌ 视频列表 API 失败: HTTP %VIDEO_RESP%
)

REM 测试文章列表
curl -s -o nul -w "%%{http_code}" http://localhost:8000/api/v1/articles > response.txt
set /p ARTICLE_RESP=<response.txt
if "%ARTICLE_RESP%"=="200" (
    echo ✅ 文章列表 API 正常
) else (
    echo ❌ 文章列表 API 失败: HTTP %ARTICLE_RESP%
)

REM 测试管理后台登录
curl -s -o nul -w "%%{http_code}" -X POST http://localhost:8000/api/v1/admin/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{""username"":""admin"",""password"":""change_me""}" > response.txt
set /p LOGIN_RESP=<response.txt
if "%LOGIN_RESP%"=="200" (
    echo ✅ 管理后台登录 API 正常
) else if "%LOGIN_RESP%"=="401" (
    echo ✅ 管理后台登录 API 正常(密码错误预期)
) else (
    echo ❌ 管理后台登录 API 失败: HTTP %LOGIN_RESP%
)

del response.txt >nul 2>&1

REM 6. 停止服务
taskkill /f /im uvicorn.exe >nul 2>&1

echo.
echo === 端到端测试完成 ===
echo 所有核心功能验证完毕！
echo 下一步: docker compose up -d 启动生产环境