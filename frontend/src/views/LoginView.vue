<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const mode = ref('login')
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

function errText(e) {
  const d = e.response?.data?.detail
  if (Array.isArray(d)) return d[0]?.msg || '输入不合法'
  return d || '操作失败，请重试'
}

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (mode.value === 'login') {
      await auth.login(username.value, password.value)
    } else {
      await api.post('/auth/register', { username: username.value, password: password.value })
      await auth.login(username.value, password.value)
    }
    router.push('/')
  } catch (e) {
    error.value = errText(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth">
    <div class="auth__panel fade-up">
      <div class="brand">FORCE<span>LAB</span></div>
      <h1 class="auth__title">{{ mode === 'login' ? '登录' : '注册' }}</h1>
      <p class="muted">进入你的力量计划</p>

      <form @submit.prevent="submit">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" required minlength="3" autocomplete="username" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" required minlength="6" autocomplete="current-password" />
        </div>

        <p v-if="error" class="auth__error">{{ error }}</p>

        <button class="btn btn--block" type="submit" :disabled="loading">
          {{ loading ? '处理中…' : mode === 'login' ? '登录' : '注册' }}
        </button>
      </form>

      <button class="auth__switch" @click="mode = mode === 'login' ? 'register' : 'login'">
        {{ mode === 'login' ? '没有账号？注册' : '已有账号？登录' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.auth {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.auth__panel {
  width: 100%;
  max-width: 400px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-top: 3px solid var(--accent);
  border-radius: var(--radius);
  padding: 40px 32px;
}

.brand {
  font-family: var(--font-display);
  font-size: 1.4rem;
  letter-spacing: 0.04em;
  color: var(--text);
  margin-bottom: 24px;
}

.brand span {
  color: var(--accent);
}

.auth__title {
  font-size: 2.6rem;
  margin-bottom: 4px;
}

.auth__panel form {
  margin-top: 28px;
}

.auth__error {
  color: var(--danger);
  font-size: 0.9rem;
  margin-bottom: 12px;
}

.btn--block {
  width: 100%;
}

.auth__switch {
  background: none;
  border: none;
  color: var(--text-muted);
  margin-top: 18px;
  width: 100%;
  font-size: 0.9rem;
  transition: color 0.15s ease;
}

.auth__switch:hover {
  color: var(--accent);
}
</style>
