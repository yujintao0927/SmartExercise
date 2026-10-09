<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const nav = [
  { to: '/admin', idx: '00', label: '数据总览' },
  { to: '/admin/users', idx: '01', label: '用户管理' },
  { to: '/admin/recommendations', idx: '02', label: '推荐记录' },
  { to: '/admin/training', idx: '03', label: '训练数据' },
  { to: '/admin/exercises', idx: '04', label: '动作库' },
  { to: '/admin/templates', idx: '05', label: '计划模板' },
  { to: '/admin/model', idx: '06', label: '模型管理' },
]

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  document.documentElement.setAttribute('data-theme', 'admin')
})
onUnmounted(() => {
  document.documentElement.removeAttribute('data-theme')
})
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="sidebar__brand">
        FORCE<em>LAB</em>
        <small>CONTROL</small>
      </div>

      <nav class="sidebar__nav">
        <router-link v-for="item in nav" :key="item.to" :to="item.to" class="nav-item">
          <span class="idx">{{ item.idx }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar__foot">
        <div class="sidebar__user">
          <div class="avatar">{{ auth.initial }}</div>
          <div class="meta">
            <div class="name">{{ auth.displayName }}</div>
            <div class="role">Admin</div>
          </div>
        </div>
        <button class="btn btn--ghost btn--block btn--sm" @click="logout">登出</button>
      </div>
    </aside>

    <main class="content">
      <div class="content__inner">
        <router-view />
      </div>
    </main>
  </div>
</template>
