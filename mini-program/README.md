# 本目录说明

`mini-program/` 为 uni-app(Vue3 + TS + @vant/weapp)小程序,同时可编译 H5。

## 环境

- Node v24.14.0 / npm 11.9.0
- uni-app 版本锁定 `vue3` 发布线:`3.0.0-5020420260813003`

## 常用命令

```bash
npm install                        # 安装依赖
npm run dev:mp-weixin              # 开发:微信小程序(用微信开发者工具导入 dist/dev/mp-weixin)
npm run build:mp-weixin            # 构建:微信小程序
npm run dev:h5                     # 开发:H5(浏览器预览)
npm run build:h5                   # 构建:H5
```

## 目录结构

```
src/
  pages.json       # 页面路由 + tabBar(5 个 tab)
  manifest.json    # 应用配置(小程序 appid 在此填写)
  uni.scss         # 全局 SCSS 变量(莫兰迪色板)
  pages/
    index/         # 欢迎页(全屏展示,2 秒后跳视频页)
    video/         # 视频标签页
    article/       # 文章标签页
    arya/          # Arya 智能助手
    mine/          # 我的(登录/优惠券/联系)
  static/          # 静态资源(tab 图标等)
```

## 注意

- `manifest.json` 的 `mp-weixin.appid` 需填你的小程序 AppID。
- @vant/weapp 需按 Vant 官方文档在微信开发者工具里配置 `usingComponents` 或按需引入。
- tabBar 图标 `static/tab-*.png` 尚未提供,需补充设计稿(design-system.md 规范)。
