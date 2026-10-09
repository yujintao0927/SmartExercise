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
    router.push(auth.isAdmin ? '/admin' : '/')
  } catch (e) {
    error.value = errText(e)
  } finally {
    loading.value = false
  }
}

function useDemo(which) {
  username.value = which
  password.value = '123456'
  mode.value = 'login'
}
</script>

<template>
  <div class="auth">
    <div class="auth__visual">
      <div class="brand">FORCE<em>LAB</em></div>
      <div class="headline">训练<br />由数据<em>驱动</em></div>
      <div>
        <p class="sub">基于机器学习的健身计划推荐系统 —— 输入 9 项特征，生成专属于你的力量计划。</p>
      </div>
    </div>

    <div class="auth__form-side">
      <div class="auth__panel">
        <h1>{{ mode === 'login' ? '登录' : '注册' }}</h1>
        <p>{{ mode === 'login' ? '进入你的力量计划' : '创建账号开始训练' }}</p>

        <form @submit.prevent="submit">
          <div class="field">
            <label>用户名</label>
            <input v-model="username" required minlength="3" autocomplete="username" placeholder="username" />
          </div>
          <div class="field">
            <label>密码</label>
            <input v-model="password" type="password" required minlength="6" autocomplete="current-password" placeholder="••••••" />
          </div>

          <p v-if="error" class="error-text" style="margin-bottom: 14px">{{ error }}</p>

          <button class="btn btn--block" type="submit" :disabled="loading">
            {{ loading ? '处理中…' : mode === 'login' ? '登录' : '注册并登录' }}
          </button>
        </form>

        <button class="auth__switch" @click="mode = mode === 'login' ? 'register' : 'login'">
          {{ mode === 'login' ? '没有账号？注册' : '已有账号？登录' }}
        </button>

        <div style="margin-top: 26px; border-top: 1px solid var(--line); padding-top: 16px">
          <p class="mono" style="font-size: 0.68rem; letter-spacing: 0.12em; color: var(--text-faint); margin-bottom: 10px">
            演示账号（密码任意）
          </p>
          <div style="display: flex; gap: 8px">
            <button class="btn btn--ghost btn--sm" @click="useDemo('demo')">会员 demo</button>
            <button class="btn btn--ghost btn--sm" @click="useDemo('admin')">管理员 admin</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
