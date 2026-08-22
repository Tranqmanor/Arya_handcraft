# Arya_handcraft · Cloudflare Pages 部署指南

> H5(顾客端)与管理后台(店主端)均部署到 Cloudflare Pages;后端 API 已在 Railway(见 `railway.toml`)。

## 0. 架构总览

| 应用 | 仓库目录 | 构建命令 | 输出目录 | Pages 项目名(建议) |
|---|---|---|---|---|
| H5 顾客端 | `mini-program/` | `npm ci && npm run build:h5` | `dist/build/h5` | `arya-h5` |
| 管理后台 | `admin-web/` | `npm ci && npm run build` | `dist` | `arya-admin` |

> ⚠️ 一个 Pages 项目只能绑定一个输出目录,因此需要创建 **两个** Pages 项目。

## 1. 方式 A:Git 集成(推荐,push 自动部署)

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com) → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**,授权并选择本 GitHub 仓库(`Tranqmanor/Arya_handcraft`,分支 `main`)。
2. 项目一(H5):
   - **Project name**: `arya-h5`
   - **Production branch**: `main`
   - **Framework preset**: 无(None)
   - **Build command**: `npm ci && npm run build:h5`
   - **Build output directory**: `dist/build/h5`
   - **Root directory(高级)**: `mini-program`
   - **Environment variables**(生产+预览都加):
     - `NODE_VERSION` = `20`
     - `VITE_API_BASE` = `https://aryahandcraft-production.up.railway.app/api/v1`(已在 `.env.production` 内置,此处可不填)
3. 项目二(管理后台):再次 Create application → Pages → 选同一仓库:
   - **Project name**: `arya-admin`
   - **Build command**: `npm ci && npm run build`
   - **Build output directory**: `dist`
   - **Root directory(高级)**: `admin-web`
   - **Environment variables**:
     - `NODE_VERSION` = `20`
     - `VITE_API_BASE` = `https://aryahandcraft-production.up.railway.app/api/v1`(已在 `.env.production` 内置)
4. 保存并 Deploy。此后每次 push 到 `main` 自动重新部署。

## 2. 方式 B:Wrangler CLI 直传(无 Git 集成时)

```bash
# 一次性登录(浏览器授权)
npx wrangler login

# 创建项目(首次)
npx wrangler pages project create arya-h5   --production-branch main
npx wrangler pages project create arya-admin --production-branch main

# 本地构建
cd mini-program && npm ci && npm run build:h5 && cd ..
cd admin-web   && npm ci && npm run build    && cd ..

# 直传(生产环境)
npx wrangler pages deploy mini-program/dist/build/h5 --project-name arya-h5   --branch main
npx wrangler pages deploy admin-web/dist             --project-name arya-admin --branch main
```

## 3. 部署后必做:后端 CORS 白名单

后端已按环境收敛 CORS(见 `server/app/main.py`)。拿到 Pages 域名后(形如 `https://arya-h5.pages.dev`),在 **Railway 服务变量** 中追加/确认:

```
ENV=prod
CORS_ORIGINS=https://arya-h5.pages.dev,https://arya-admin.pages.dev
```

> 不配置会导致浏览器端跨域被拦截(H5 页面与后台接口全部请求失败)。
> 自定义域名绑定后,把正式域名也追加进 `CORS_ORIGINS` 并重启服务。

## 4. 常见问题

- **后台刷新 404**:`admin-web/public/_redirects` 已提供 SPA 回退(`/* → /index.html 200`),随构建自动进入 `dist`;若自行改了输出结构需保留该文件。
- **接口请求打到 Pages 自身域名**:`VITE_API_BASE` 未生效。检查 Pages 环境变量与 `.env.production`;修改环境变量后需 **Retry deploy** 才会注入新值。
- **构建 OOM / vue-tsc 失败**:确认 `NODE_VERSION=20`;必要时可将构建命令改为 `npm ci && npx vite build`(跳过类型检查,不建议长期)。
- **自定义域名**:Pages 项目 → Custom domains 绑定后,同步更新 `CORS_ORIGINS`。

## 5. 旧方案说明

根目录原 `netlify.toml`(Netlify 预构建资产方案)已随本次迁移删除;如需回顾可在 git 历史中找到。
