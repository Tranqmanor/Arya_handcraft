// App 全局状态(pinia):订单数据 + 当前页面 + 当前 Tab
import { defineStore } from 'pinia'

import { loadOrders, saveOrders } from '@/local/store'
import type { LocalOrder } from '@/local/types'

export type TabKey = 'home' | 'manage' | 'stats' | 'mine'

/** 内页:tab 之外的全屏页 */
export type AppPage = 'tabs' | 'orders' | 'articles' | 'videos' | 'carousel' | 'coupons'

export const useAppStore = defineStore('app', {
  state: () => ({
    orders: loadOrders() as LocalOrder[],
    /** 当前展示页:tab 四页之外的内页 */
    page: 'tabs' as AppPage,
    /** 当前激活的 Tab */
    activeTab: 'home' as TabKey,
    /** 管理员登录态(全局门禁) */
    loggedIn: localStorage.getItem('arya_admin_logged') === '1',
    /** 从账单钻取跳转时,订单页需自动打开详情的订单 id */
    focusOrderId: null as string | null,
  }),
  getters: {
    /** 排队中订单(定金已付、尾款未付),按下单时间序 */
    queued(state): LocalOrder[] {
      return state.orders.filter((o) => o.depositPaid && !o.finalPaid)
    },
  },
  actions: {
    persist() {
      saveOrders(this.orders)
    },
    addOrder(order: LocalOrder) {
      this.orders = [...this.orders, order]
      this.persist()
    },
    addOrders(newOrders: LocalOrder[]) {
      this.orders = [...this.orders, ...newOrders]
      this.persist()
    },
    updateOrder(order: LocalOrder) {
      this.orders = this.orders.map((o) => (o.id === order.id ? order : o))
      this.persist()
    },
    removeOrder(id: string) {
      this.orders = this.orders.filter((o) => o.id !== id)
      this.persist()
    },
    reload() {
      this.orders = loadOrders()
    },
    /** 切换 Tab 并可选地进入某内页 */
    goto(tab: TabKey, page: AppPage = 'tabs') {
      this.activeTab = tab
      this.page = page
    },
    /** 跳到订单页并自动打开某订单详情(账单钻取用) */
    focusOrder(id: string) {
      this.focusOrderId = id
      this.goto('manage', 'orders')
    },
    login() {
      this.loggedIn = true
      localStorage.setItem('arya_admin_logged', '1')
    },
    logout() {
      this.loggedIn = false
      localStorage.setItem('arya_admin_logged', '0')
      localStorage.removeItem('admin_token')
    },
  },
})