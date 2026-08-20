# Arya_handcraft · 接口文档

> 以 OpenAPI(`/docs`)为准;本文件为常用接口速查与示例。后续里程碑不断补充。
> Base URL: `/api/v1` | 认证方式:`Authorization: Bearer <access_token>`

## 1. 认证 Auth

### `POST /auth/login` 微信一键登录
- 请求:
  ```json
  { "code": "wx.login() 返回的 code" }
  ```
- 响应 `200`:
  ```json
  {
    "access_token": "<jwt>",
    "refresh_token": "<jwt>",
    "token_type": "bearer"
  }
  ```
- 说明:code 经后端 `code2session` 换 openid;新用户自动创建并发放新客券。
- 错误:`400`(code 无效)、`500`(微信未配置)。

### `POST /auth/refresh` 刷新 token
- 请求:
  ```json
  { "refresh_token": "<jwt>" }
  ```
- 响应:同 login。

## 2. 用户 Users(需登录)

### `GET /users/me` 获取当前用户
### `PUT /users/me` 更新资料
- 请求(皆为可选字段):
  ```json
  { "nickname": "阿茶", "avatar_url": "https://x.png", "phone": "138****0000" }
  ```

### `GET /users/me/coupons` 我的优惠券列表
- 响应:coupon 数组(含 title/amount/status/expires_at)。

## 3. 视频 Videos

### `GET /videos` 视频列表(公开)
- 响应:已发布视频数组(按 sort_order 排序)
  ```json
  [{
    "id": 1,
    "title": "橘猫小铃铛制作过程",
    "description": "",
    "video_url": "https://r2.example.com/v1.mp4",
    "cover_url": "",
    "duration": 45,
    "view_count": 128,
    "sort_order": 0,
    "created_at": "2026-08-18T00:00:00Z"
  }]
  ```

### `GET /videos/{id}` 视频详情(公开)

### `POST /videos/{id}/view` 浏览量上报(公开)
- 请求:
  - Header 可选 `Authorization: Bearer <token>`(已登录则按用户去重)
  - Query 参数 `viewer_key`(未登录设备指纹)
- 响应:
  ```json
  { "video_id": 1, "view_count": 129, "viewed": true }
  ```
- 说明:`viewed=true` 表示本次计为新增浏览量;同一用户/设备对同一视频仅计 1 次。

## 4. 文章 Articles

### `GET /articles` 文章列表(公开)
- 响应:已发布文章列表(不含正文),含 title/summary/cover_url/category/view_count。
- `category`: `photo_guide`=定制拍照指南,`general`=普通文章。

### `GET /articles/{id}` 文章详情(公开)
- 响应:含 `content`(Markdown 文本,前端渲染)。

### `POST /articles/{id}/view` 文章浏览量 +1(公开)
- 响应:`{ "article_id": 1, "view_count": 1, "viewed": true }`
- 说明:文章浏览为简单计数,不做去重。

## 5. 联系 Contact

### `GET /contact/config` 联系配置(公开)
- 响应:
  ```json
  {
    "qr_url": "",
    "tip": "长按识别二维码,添加店主微信进行咨询",
    "nickname": "Arya 手作毛毡"
  }
  ```
- 说明:前端默认展示内置二维码(static/wechat-qr.png);`qr_url` 可配置 CDN 二维码。

## 6. Arya 智能助手(需登录)

### `POST /arya/chat` 对话(需登录)
- 请求:
  ```json
  { "message": "定制一只毛毡猫多少钱呀?" }
  ```
- 响应:
  ```json
  {
    "reply": "想给猫猫定制一只专属毛毡猫咪吗?具体的价格和工期由店主来沟通最准哦,我帮你呼叫一下店主吧~",
    "intent": "call_master",
    "call_master_hint": "点击下方按钮,添加店主微信咨询吧~"
  }
  ```
- 说明:
  - `intent`:`call_master`(呼叫主人)/ `info`(信息咨询)/ `smalltalk`(闲聊)
  - `call_master` 时前端自动弹出「联系店主」二维码交互
  - 对话会存入 `ai_messages`,作为长期记忆(最近 20 条作为上下文)

### `DELETE /arya/sessions` 清空记忆(需登录)
- 响应:`{ "detail": "已清空对话记忆" }`

## 7. 系统

### `GET /health` 健康检查
- 返回 `{"status":"ok","database":"ok"}`

## 8. 通用错误格式

```json
{ "detail": "错误描述" }
```
常见状态码:
- `401` 未登录 / token 失效
- `400` 参数或业务错误
- `404` 资源不存在
- `500` 服务端错误

## 待补充(后续里程碑)
- M3 视频:videos 列表/详情、浏览量上报
- M4 文章:articles 列表/详情
- M5 联系:contact/二维码
- M6 Arya:ai/chat(意图识别 + DeepSeek)
- M8 管理后台:admin/auth、admin/coupons 等
