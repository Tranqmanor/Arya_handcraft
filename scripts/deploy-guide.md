# Arya_handcraft 生产环境部署指南

## 快速开始

### 1. 准备环境变量
```bash
cd server
cp .env.example .env
# 编辑 .env 文件，填写生产环境配置:
# - 数据库连接串(如果使用外部数据库)
# - JWT_SECRET (使用安全的随机密钥)
# - 微信小程序 AppID/AppSecret
# - 大模型 API Key
# - 管理后台初始密码
```

### 2. 一键启动生产环境
```bash
docker compose -f docker-compose.prod.yml up -d
```

### 3. 查看服务状态
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f api
```

## 服务访问地址

- **API 服务**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 环境变量配置

### 必需配置
```env
# 数据库连接(如果使用外部数据库)
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname

# JWT 密钥(生成命令: openssl rand -hex 64)
JWT_SECRET=your_secure_random_jwt_secret

# 微信小程序配置
WX_APP_ID=your_app_id
WX_APP_SECRET=your_app_secret

# 大模型配置
LLM_API_KEY=your_llm_api_key
```

### 可选配置
```env
# 联系二维码 URL
CONTACT_QR_URL=https://example.com/qr.png

# 管理后台初始密码
ADMIN_INIT_PASSWORD=secure_password

# 日志级别
LOG_LEVEL=INFO
```

## 维护命令

### 查看日志
```bash
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs db
docker compose -f docker-compose.prod.yml logs redis
```

### 重启服务
```bash
docker compose -f docker-compose.prod.yml restart api
```

### 更新代码后重新部署
```bash
docker compose -f docker-compose.prod.yml build api
docker compose -f docker-compose.prod.yml up -d --force-recreate api
```

### 停止所有服务
```bash
docker compose -f docker-compose.prod.yml down
```

## 数据库管理

### 备份数据库
```bash
docker compose -f docker-compose.prod.yml exec db pg_dump -U arya arya_handcraft > backup_$(date +%Y%m%d).sql
```

### 恢复数据库
```bash
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U arya arya_handcraft
```

### 进入数据库控制台
```bash
docker compose -f docker-compose.prod.yml exec db psql -U arya arya_handcraft
```

## 监控与健康检查

### 健康检查端点
```bash
curl http://localhost:8000/health
```

### 服务状态检查
```bash
# 检查 API 服务
curl -f http://localhost:8000/docs > /dev/null 2>&1 && echo "API OK" || echo "API Down"

# 检查数据库连接
docker compose -f docker-compose.prod.yml exec db pg_isready -U arya

# 检查 Redis 连接
docker compose -f docker-compose.prod.yml exec redis redis-cli ping
```

## 故障排除

### 常见问题
1. **端口冲突**:修改 docker-compose.prod.yml 中的端口映射
2. **数据库连接失败**:检查 .env 中的 DATABASE_URL
3. **内存不足**:增加 Docker 资源分配或优化容器配置

### 查看容器资源使用
```bash
docker stats $(docker compose -f docker-compose.prod.yml ps -q)
```