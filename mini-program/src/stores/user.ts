import { defineStore } from 'pinia'
import { getMe, loginWithCode, type UserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    isLoggedIn: false,
    user: null as UserInfo | null,
  }),
  getters: {
    nickname: (state) => state.user?.nickname || '微信用户',
    avatar: (state) => state.user?.avatar_url || '',
  },
  actions: {
    /** 微信一键登录 */
    async wxLogin() {
      // 1. 获取微信登录 code
      const code = await this._getWxCode()
      // 2. 后端换 token
      const token = await loginWithCode(code)
      uni.setStorageSync('access_token', token.access_token)
      uni.setStorageSync('refresh_token', token.refresh_token)
      this.isLoggedIn = true
      // 3. 拉取用户信息
      await this.fetchUser()
    },

    async fetchUser() {
      const user = await getMe()
      this.user = user
      this.isLoggedIn = true
      return user
    },

    async logout() {
      uni.removeStorageSync('access_token')
      uni.removeStorageSync('refresh_token')
      this.isLoggedIn = false
      this.user = null
    },

    updateUser(user: UserInfo) {
      this.user = user
    },

    _getWxCode(): Promise<string> {
      return new Promise((resolve, reject) => {
        // #ifdef MP-WEIXIN
        uni.login({
          provider: 'weixin',
          success: (res) => resolve(res.code || ''),
          fail: (err) => reject(new Error(err.errMsg)),
        })
        // #endif
        // #ifndef MP-WEIXIN
        // H5 调试:无微信 code,给个占位值(无法真正登录,仅页面展示用)
        resolve('h5-debug-placeholder')
        // #endif
      })
    },
  },
})