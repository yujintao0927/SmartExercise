<script setup>
import { ref } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const pwdForm = ref({ old_password: '', new_password: '' })
const msg = ref('')
const error = ref('')
const saving = ref(false)

async function changePassword() {
  msg.value = ''
  error.value = ''
  saving.value = true
  try {
    await api.put('/auth/password', pwdForm.value)
    msg.value = '密码已更新'
    pwdForm.value = { old_password: '', new_password: '' }
  } catch (e) {
    error.value = e.response?.data?.detail || '修改失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Account</span>
      <h1>个人<em>中心</em></h1>
      <p>查看账号信息并管理密码。</p>
    </div>

    <div class="panel panel--accent reveal reveal-1">
      <div class="panel__head"><h3>账号信息</h3></div>
      <div class="panel__body">
        <div style="display: flex; align-items: center; gap: 16px">
          <div class="avatar" style="width: 52px; height: 52px; font-size: 1.4rem">{{ auth.initial }}</div>
          <div>
            <div style="font-size: 1.3rem; font-weight: 700">{{ auth.displayName }}</div>
            <div class="mono" style="font-size: 0.72rem; letter-spacing: 0.1em; color: var(--accent)">MEMBER</div>
          </div>
        </div>
        <div style="display: flex; gap: 40px; margin-top: 22px; padding-top: 18px; border-top: 1px solid var(--line)">
          <div><span class="muted">用户名</span><div>{{ auth.user?.username }}</div></div>
          <div><span class="muted">角色</span><div>会员</div></div>
          <div><span class="muted">注册时间</span><div class="mono">{{ auth.user?.created_at?.slice(0, 10) || '—' }}</div></div>
        </div>
      </div>
    </div>

    <form class="panel reveal reveal-2" style="margin-top: 16px; padding: 24px" @submit.prevent="changePassword">
      <h3 style="font-size: 1rem; margin-bottom: 18px">修改密码</h3>
      <div style="max-width: 380px">
        <div class="field">
          <label>旧密码</label>
          <input v-model="pwdForm.old_password" type="password" required autocomplete="current-password" />
        </div>
        <div class="field">
          <label>新密码</label>
          <input v-model="pwdForm.new_password" type="password" required minlength="6" autocomplete="new-password" />
        </div>
      </div>
      <p v-if="msg" style="color: var(--ok); margin-bottom: 14px">{{ msg }}</p>
      <p v-if="error" class="error-text" style="margin-bottom: 14px">{{ error }}</p>
      <button class="btn" type="submit" :disabled="saving">{{ saving ? '保存中…' : '更新密码' }}</button>
    </form>
  </div>
</template>
