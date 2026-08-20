# 本目录说明

`admin-web/` 为管理后台(Vue3 + TypeScript + Element Plus + Pinia + Vue Router)。

## 常用命令

```bash
npm install
npm run dev        # 开发:http://localhost:5174(已配置 /api 代理到 localhost:8000)
npm run build      # 构建
npm run preview
```

## 目录结构

```
src/
  main.ts           # 入口(Element Plus 中文语言包)
  App.vue
  router/           # 路由(login / dashboard,基础守卫)
  stores/           # Pinia
  api/http.ts       # axios 封装(token 注入 + 统一错误)
  views/
    LoginView.vue   # 登录页
    DashboardView.vue  # 后台布局骨架(视频/文章/优惠券/用户导航位)
```

## 说明

- 登录接口暂为占位,待 M8 对接 `POST /api/v1/admin/auth/login`。
- 管理后台独立部署(Cloudflare Pages),见 docs/deploy.md。
