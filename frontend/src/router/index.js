import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('../components/UserLayout.vue'),
    meta: { requiresAuth: true, userOnly: true },
    children: [
      { path: '', name: 'home', component: () => import('../views/UserHome.vue') },
      { path: 'profile', name: 'profile', component: () => import('../views/ProfileView.vue') },
      { path: 'plan', name: 'plan', component: () => import('../views/PlanView.vue') },
      { path: 'recommend', name: 'recommend', component: () => import('../views/RecommendView.vue') },
      { path: 'training', name: 'training', component: () => import('../views/TrainingView.vue') },
      { path: 'body', name: 'body', component: () => import('../views/BodyView.vue') },
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'account', name: 'account', component: () => import('../views/AccountView.vue') },
    ],
  },
  {
    path: '/admin',
    component: () => import('../components/AdminLayout.vue'),
    meta: { requiresAuth: true, adminOnly: true },
    children: [
      { path: '', name: 'admin-overview', component: () => import('../views/AdminOverview.vue') },
      { path: 'users', name: 'admin-users', component: () => import('../views/AdminUsers.vue') },
      { path: 'recommendations', name: 'admin-recommendations', component: () => import('../views/AdminRecommendations.vue') },
      { path: 'training', name: 'admin-training', component: () => import('../views/AdminTraining.vue') },
      { path: 'exercises', name: 'admin-exercises', component: () => import('../views/AdminExercises.vue') },
      { path: 'templates', name: 'admin-templates', component: () => import('../views/AdminTemplates.vue') },
      { path: 'model', name: 'admin-model', component: () => import('../views/AdminModel.vue') },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const role = JSON.parse(localStorage.getItem('user') || 'null')?.role

  if (to.meta.requiresAuth && !token) return '/login'
  if (to.path === '/login' && token) return role === 'admin' ? '/admin' : '/'
  if (to.meta.adminOnly && role !== 'admin') return '/'
  if (to.meta.userOnly && role === 'admin') return '/admin'
})

export default router
