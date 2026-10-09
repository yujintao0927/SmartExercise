import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'home', component: () => import('../views/HomeView.vue') },
      { path: 'profile', name: 'profile', component: () => import('../views/ProfileView.vue') },
      { path: 'recommend', name: 'recommend', component: () => import('../views/RecommendView.vue') },
      { path: 'training', name: 'training', component: () => import('../views/TrainingView.vue') },
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'admin', name: 'admin', component: () => import('../views/AdminView.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) return '/login'
  if (to.path === '/login' && token) return '/'
})

export default router
