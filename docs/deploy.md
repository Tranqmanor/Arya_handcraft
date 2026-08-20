# Arya_handcraft · 部署文档

> 对应 preplan.md 第 9 节;本地 / 开发 / 生产三套环境。版本 v1.0(2026-08-18)

## 1. 环境概览

| 环境 | 后端 API | 数据库/缓存 | 前端 | 用途 |
|---|---|---|---|---|
| 本地 | uvicorn(本机) | docker-compose(PG+Redis) | uni-app H5 dev | 开发调试 |
| 开发(免备案) | Render/Railway 免费档 | Neon/Supabase + Upstash | Cloudflare Pages(H5/后台) | 打样验证业务 |
| 生产(小程序正式版) | 腾讯云轻量 + Docker(备案域名)或微信云托管 | 同机 PG/Redis 或托管 | 微信小程序提审 | 正式上线 |

## 2. 本地环境

```bash
cd server
cp .env.example .env          # 首次;按需修改 JWT_SECRET 等
docker compose up -d db redis # 数据库与 Redis
pip install -r requirements.txt
alembic upgrade head          # 建表
uvicorn app.main:app --reload # http://localhost:8000/docs
```

## 3. 开发环境(免备案,Cloudflare 路线)

> 目标:¥0,先用起来。详见 preplan 9.2。

1. **PostgreSQL**:注册 Neon(或 Supabase),创建项目,复制连接串。
2. **Redis**:注册 Upstash,创建 Redis,复制 REST/连接地址。
3. **后端**:Git 仓库推送到 GitHub,在 Render(或 Railway)New → Web Service 关联仓库,目录选 `server/`,启动命令:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   环境变量按 `.env.example` 填齐(DATABASE_URL 用 Neon 串、REDIS_URL 用 Upstash 串)。
4. **前端 H5 / 管理后台**:Cloudflare Pages 关联仓库 → 构建命令 `npm run build` → 输出目录 `dist` → 环境变量 `VITE_API_BASE` 指向后端 HTTPS 域名。
5. **视频**:Cloudflare R2 建桶 → 上传 mp4 → 公开访问 URL。

## 4. 生产环境(小程序正式版,需备案,后期)

> 小程序正式版 `request` 合法域名必须 HTTPS + ICP 备案。路线 A(个人备案 + 轻量服务器)推荐。

1. 注册域名,在服务器商提交 ICP 备案(个人可备案,1~2 周)。
2. 购买轻量应用服务器(2核2G,约 ¥50~100/年),Ubuntu 22.04。
3. 部署:
   ```bash
   git clone <repo> /opt/arya && cd /opt/arya/server
   cp .env.example .env        # 填生产配置
   docker compose up -d        # fastapi + postgres + redis
   alembic upgrade head
   ```
4. Nginx 反代 + HTTPS(免费证书,Let's Encrypt 或云厂商免费 SSL)。
5. 微信公众平台:开发管理 → 服务器域名 → 添加 `https://api.yourdomain.com` 到 `request` 合法域名。
6. 小程序开发者工具取消「不校验合法域名」,提审发布。

## 5. 运维清单

- 数据备份:生产库每日 `pg_dump` 到 COS/本地。
- 监控:`/health` 探活;后端日志定期检查;关注 LLM API 用量。
- 升级:改模型后 `alembic revision --autogenerate` + `alembic upgrade head`。
- 免费档注意:Render/Neon 实例休眠冷启动 1~30 秒;超量会暂停,关注用量。
