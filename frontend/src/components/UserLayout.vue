<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const nav = [
  { to: '/', idx: '00', label: '首页' },
  { to: '/profile', idx: '01', label: '个人画像' },
  { to: '/plan', idx: '02', label: '训练计划' },
  { to: '/recommend', idx: '03', label: '智能推荐' },
  { to: '/training', idx: '04', label: '训练打卡' },
  { to: '/body', idx: '05', label: '身体数据' },
  { to: '/dashboard', idx: '06', label: '数据看板' },
  { to: '/account', idx: '07', label: '个人中心' },
]

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  document.documentElement.removeAttribute('data-theme')
})
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="sidebar__brand">
        FORCE<em>LAB</em>
        <small>MEMBER</small>
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
            <div class="role">Member</div>
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
