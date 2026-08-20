import { defineConfig } from 'vite'
// @dcloudio/vite-plugin-uni 为 CJS 包,Node 24 下 default import 拿到的是模块对象,
// 需解包获取真正的插件函数
import uniModule from '@dcloudio/vite-plugin-uni'

const uni = (uniModule as unknown as { default: typeof uniModule }).default || uniModule

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [uni() as any],
})
