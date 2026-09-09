import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  base: './', // 移动端/WebView 以相对路径加载,避免安卓壳内路径问题
  server: {
    host: '127.0.0.1',
    port: 5300, // 本机 5141-5240 被 Windows 保留,选 5300(已验证不在排除段)
    proxy: {
      // 开发环境代理到本地 FastAPI
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})