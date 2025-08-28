import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: '首页' }
    },
    {
      path: '/roots',
      name: 'roots',
      component: () => import('../views/roots/RootsView.vue'),
      meta: { title: '词根管理' }
    },
    {
      path: '/fields',
      name: 'fields',
      component: () => import('../views/fields/FieldsView.vue'),
      meta: { title: '字段管理' }
    },
    {
      path: '/models',
      name: 'models',
      component: () => import('../views/models/ModelsView.vue'),
      meta: { title: '模型管理' }
    }
  ],
})

export default router
