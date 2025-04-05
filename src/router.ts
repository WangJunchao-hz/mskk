import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: "/config"
  },
  {
    name: 'config',
    path: '/config',
    component: () => import('@/view/config.vue'),
    meta: {
      title: 'VIP 偷卡'
    }
  }
]

const router = createRouter({
  routes,
  history: createWebHashHistory()
})

router.beforeEach((to, from, next) => {
  const title = to?.meta?.title
  if (title) {
    document.title = title as string
  }
  next()
})

export default router
