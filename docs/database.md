# Arya_handcraft · 数据库设计文档

> 对应 preplan.md 第 5 节;本文件为字段级说明,以代码(server/app/models + alembic 迁移)为准。
> 版本 v1.0(2026-08-18)

## 1. 关系总览(ER)

```
users 1 ──── * coupons
users 1 ──── * ai_messages
videos 1 ──── * video_views
admin_users   (独立,管理后台)
```

## 2. 表结构

### 2.1 users 用户(个人主体 → 手机号自填)
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint PK | 自增主键 |
| openid | varchar(64) UK | 微信 openid,登录凭证 |
| unionid | varchar(64) UK | 微信 unionid(可选) |
| nickname | varchar(64) | 昵称(头像昵称填写能力/自填) |
| avatar_url | text | 头像地址 |
| phone | varchar(20) UK | 手机号(**自填、可选**,个人主体无快捷接口) |
| created_at / updated_at | timestamptz | 时间戳 |

### 2.2 coupons 优惠券
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint PK | |
| user_id | bigint FK→users | 所属用户 |
| title | varchar(64) | 券名,如「新客立减 20」 |
| amount | numeric(10,2) | 面额(元) |
| status | varchar(16) | unused / used / expired |
| expires_at / used_at | timestamptz | 过期/核销时间 |
| created_at | timestamptz | |
- 索引:`(user_id, status)`
- 发放:新客注册自动 1 张(后端逻辑)+ 后台手动(`POST /admin/coupons/grant`)

### 2.3 videos 视频
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint PK | |
| title | varchar(128) | 标题 |
| description | text | 描述 |
| video_url | text | 竖屏 mp4 地址(**Cloudflare R2**) |
| cover_url | text | 封面图 |
| duration | int | 时长(秒),前端展示 mm:ss |
| view_count | int | 浏览量(冗余计数) |
| is_published | boolean | 是否发布 |
| sort_order | int | 排序 |
| created_at | timestamptz | |

### 2.4 video_views 浏览量去重(防刷)
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint PK | |
| video_id | bigint FK→videos | |
| viewer_key | varchar(128) | openid 或会话指纹 |
| created_at | timestamptz | |
- 唯一约束:`(video_id, viewer_key)`

### 2.5 articles 文章
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint PK | |
| title | varchar(128) | |
| summary | varchar(256) | 摘要 |
| cover_url | text | |
| content | text | 富文本/Markdown 图文 |
| category | varchar(32) | photo_guide=拍照指南,general=普通 |
| view_count | int | |
| is_published | boolean | |
| sort_order | int | |
| created_at / updated_at | timestamptz | |

### 2.6 ai_messages Arya 对话(长期记忆)
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint PK | |
| user_id | bigint FK→users | |
| role | varchar(16) | user / assistant |
| content | text | 消息内容 |
| intent | varchar(32) | call_master / info / smalltalk(assistant 侧) |
| created_at | timestamptz | |
- 索引:`(user_id, created_at)`
- 每次对话取最近 N(如 20)条作为上下文;v3 可加 pgvector 向量记忆

### 2.7 admin_users 管理员(独立)
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint PK | |
| username | varchar(64) UK | 登录名 |
| password_hash | varchar(256) | bcrypt 哈希 |
| created_at / updated_at | timestamptz | |

## 3. 预留表(后续里程碑)
- orders 订单、addresses 邮寄地址(M10+)
- 收款:个人主体无微信支付 → 引导微信转账,订单金额字段预留

## 4. 迁移策略
- 使用 Alembic:本地 `alembic upgrade head`;生产环境在部署时执行
- 新改动先改 `models/`,再 `alembic revision --autogenerate -m "desc"` 生成迁移,人工 review 后升级
- 破坏性变更(删列/改类型)需提供数据迁移脚本
