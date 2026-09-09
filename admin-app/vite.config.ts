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
    host: '127.0.0.1', // 避开 ::1 解析
    port: 5180, // 5175 常被 Windows(Hyper-V/WinNAT)保留导致 EACCES
    proxy: {
      // 开发环境代理到本地 FastAPI
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})