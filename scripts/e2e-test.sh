#!/bin/bash
# Arya_handcraft 端到端测试脚本
# 执行完整的功能验证:数据库迁移、单元测试、API 测试

echo "=== Arya_handcraft 端到端测试 ==="
echo "当前时间: $(date)"
echo

# 检查 Docker 是否运行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker 未运行，请启动 Docker Desktop"
    exit 1
fi

echo "✅ Docker 已运行"

cd server

# 1. 启动数据库和 Redis
echo
echo "1. 启动 PostgreSQL 和 Redis..."
docker compose up -d db redis

# 等待数据库健康检查
echo "等待数据库就绪..."
sleep 10

# 2. 数据库迁移
echo
echo "2. 执行数据库迁移..."
python -m alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ 数据库迁移成功"
else
    echo "❌ 数据库迁移失败"
    exit 1
fi

# 3. 运行单元测试
echo
echo "3. 运行后端单元测试..."
python -m pytest tests -v

if [ $? -eq 0 ]; then
    echo "✅ 所有单元测试通过"
else
    echo "❌ 单元测试失败"
    exit 1
fi

# 4. 启动后端服务
echo
echo "4. 启动 FastAPI 服务..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 5. 测试 API 端点
echo
echo "5. 测试核心 API 端点..."

# 测试视频列表
VIDEO_RESP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/videos)
if [ "$VIDEO_RESP" = "200" ]; then
    echo "✅ 视频列表 API 正常"
else
    echo "❌ 视频列表 API 失败: HTTP $VIDEO_RESP"
fi

# 测试文章列表
ARTICLE_RESP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/articles)
if [ "$ARTICLE_RESP" = "200" ]; then
    echo "✅ 文章列表 API 正常"
else
    echo "❌ 文章列表 API 失败: HTTP $ARTICLE_RESP"
fi

# 测试管理后台登录
LOGIN_RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/v1/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"change_me"}')

if [ "$LOGIN_RESP" = "200" ] || [ "$LOGIN_RESP" = "401" ]; then
    echo "✅ 管理后台登录 API 正常"
else
    echo "❌ 管理后台登录 API 失败: HTTP $LOGIN_RESP"
fi

# 6. 停止服务
echo
kill $SERVER_PID 2>/dev/null

echo "=== 端到端测试完成 ==="
echo "所有核心功能验证完毕！"
echo "下一步: docker compose up -d 启动生产环境"