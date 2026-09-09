# 后台管理 App(admin-app)构建与安装

> 目标:安卓手机可侧载的 .apk。订单/排队/账单存手机本地;文章/轮播/视频/优惠券走线上后端。

## 一、如何获得 APK(无需本机装 Android 环境)

1. push 代码到 GitHub 后,Actions 页面 → **Build Admin APK** 工作流自动运行(约 5~10 分钟);
2. 打开该次运行 → Artifacts 里下载 **arya-admin-app-apk** → 解压得 `app-release.apk`;
3. 传到手机 → 点击安装(允许"未知来源");
4. 也可随时在 Actions 页手动 **Run workflow** 触发构建。

## 二、⚠️ 必做一次:后端 CORS 加白 App 的虚拟域

App 内 WebView 通过 `https://appassets.androidplatform.net` 虚拟域加载页面,
访问 Railway API 时 Origin 即为此值。**需要在 Railway 共享变量里更新**:

```
CORS_ORIGINS=https://arya-handcraft-h5.pages.dev,https://arya-handcraft-admin.pages.dev,https://appassets.androidplatform.net
```

(改完等 Railway 重部署 🟢)

## 三、登录说明(双模式)

- 「我的」页首次登录时输入的密码 = 设为**本地密码**(离线可进,管理本地订单);
- 同时 App 会静默用 `admin / 该密码` 调后端登录:
  - 密码与后台一致 → 在线模块自动解锁(文章/轮播/视频/优惠券可用);
  - 不一致或无网络 → 仅在线功能不可用,本地功能不受影响;
- 菜单中标了 `在线` 标签的项需要此步成功;`本地` 标签的订单信息完全离线可用。

## 四、数据与导出

- 订单数据保存在手机 App 本地存储(localStorage),**换机/卸载会丢失**;
- 导出:「管理 → 订单信息 → 导出 CSV」→ 唤起系统分享(微信/邮件保存),CSV 含 BOM,Excel 直接打开不乱码;
- 建议每周导出一份发给自己的邮箱作备份。

## 五、本地调试(可选,PC 浏览器)

```bash
cd admin-app
npm install
npm run dev   # http://localhost:5175,浏览器手机模式体验
```

## 六、结构

```
admin-app/        # Vue3 移动端工程(订单本地 + 在线 API 复用)
android-shell/    # Flutter WebView 壳(loadFlutterAsset 加载打包好的 web 产物)
.github/workflows/build-apk.yml  # CI:build web → flutter build apk → artifact
```

## 七、已知边界(v1)

- 文章正文编辑为纯文本 Markdown 输入(无图片插入按钮,R2 上传按钮暂在网页后台);
- WebView 内 `<input type=file>` 个别机型可能无响应,遇到请改用网页后台上传;
- 图标为 emoji 占位,后续可换图片资源。
