<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="layout">
    <header class="topbar">
      <div class="container topbar__inner">
        <router-link to="/" class="brand">FORCE<span>LAB</span></router-link>
        <nav class="nav">
          <router-link to="/">首页</router-link>
          <router-link to="/profile">画像</router-link>
          <router-link to="/recommend">推荐</router-link>
          <router-link to="/training">训练</router-link>
          <router-link to="/dashboard">仪表盘</router-link>
          <router-link to="/admin">管理</router-link>
        </nav>
        <button class="btn btn--ghost btn--sm" @click="logout">登出</button>
      </div>
    </header>
    <main class="container main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topbar {
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  background: rgba(10, 10, 11, 0.85);
  backdrop-filter: blur(8px);
  z-index: 10;
}

.topbar__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.brand {
  font-family: var(--font-display);
  font-size: 1.4rem;
  letter-spacing: 0.04em;
  color: var(--text);
}

.brand span {
  color: var(--accent);
}

.nav {
  display: flex;
  gap: 28px;
}

.nav a {
  color: var(--text-muted);
  font-weight: 600;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  transition: color 0.15s ease;
}

.nav a.router-link-active {
  color: var(--accent);
}

.btn--sm {
  padding: 8px 16px;
  font-size: 0.8rem;
}

.main {
  flex: 1;
  padding-top: 40px;
  padding-bottom: 64px;
}
</style>
