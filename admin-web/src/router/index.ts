import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'overview',
          component: () => import('@/views/OverviewView.vue'),
        },
        {
          path: 'videos',
          name: 'videos',
          component: () => import('@/views/VideosView.vue'),
        },
        {
          path: 'articles',
          name: 'articles',
          component: () => import('@/views/ArticlesView.vue'),
        },
        {
          path: 'coupons',
          name: 'coupons',
          component: () => import('@/views/CouponsView.vue'),
        },
      ],
    },
  ],
})

// 简单守卫:未登录跳转登录页
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('admin_token')) {
    return { name: 'login' }
  }
})

export default router
