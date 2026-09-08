// App 全局状态(pinia):订单数据 + 当前页面 + 当前 Tab
import { defineStore } from 'pinia'

import { loadOrders, saveOrders } from '@/local/store'
import type { LocalOrder } from '@/local/types'

export type TabKey = 'home' | 'manage' | 'stats' | 'mine'

export const useAppStore = defineStore('app', {
  state: () => ({
    orders: loadOrders() as LocalOrder[],
    /** 当前展示页:tab 四页之外的内页(如订单管理) */
    page: 'tabs' as 'tabs' | 'orders',
    /** 当前激活的 Tab */
    activeTab: 'home' as TabKey,
  }),
  getters: {
    /** 排队中订单(排队定金/制作定金已付、尾款未付),按录入顺序 */
    queued(state): LocalOrder[] {
      return state.orders.filter((o) => (o.depositPaid || o.makingPaid) && !o.finalPaid)
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
    goto(tab: TabKey, page: 'tabs' | 'orders' = 'tabs') {
      this.activeTab = tab
      this.page = page
    },
  },
})