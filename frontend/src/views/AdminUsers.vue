<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const users = ref([])
const search = ref('')
const roleFilter = ref('')
const detail = ref(null)
const resetMsg = ref('')

async function load() {
  const params = {}
  if (search.value) params.search = search.value
  if (roleFilter.value) params.role = roleFilter.value
  const { data } = await api.get('/admin/users', { params })
  users.value = data.items
}

async function showDetail(u) {
  const { data } = await api.get(`/admin/users/${u.id}`)
  detail.value = data
}

async function toggleStatus(u) {
  await api.patch(`/admin/users/${u.id}/status`, { active: !u.active })
  await load()
}

async function remove(u) {
  if (!confirm(`确定删除用户「${u.username}」？`)) return
  await api.delete(`/admin/users/${u.id}`)
  detail.value = null
  await load()
}

async function resetPwd(u) {
  const { data } = await api.post(`/admin/users/${u.id}/reset-password`, {})
  resetMsg.value = `已重置「${data.username}」的密码为：${data.new_password}`
  setTimeout(() => (resetMsg.value = ''), 4000)
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Users</span>
      <h1>用户<em>管理</em></h1>
      <p>查看、禁用或删除用户账号。</p>
    </div>

    <div class="panel reveal reveal-1">
      <div class="panel__body" style="display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end">
        <div class="field" style="margin: 0; flex: 1; min-width: 200px">
          <label>搜索用户名</label>
          <input v-model="search" placeholder="输入用户名" @input="load" />
        </div>
        <div class="field" style="margin: 0; min-width: 140px">
          <label>角色</label>
          <select v-model="roleFilter" @change="load">
            <option value="">全部</option>
            <option value="user">用户</option>
            <option value="admin">管理员</option>
          </select>
        </div>
      </div>
    </div>

    <p v-if="resetMsg" style="color: var(--ok); margin: 14px 0 0">{{ resetMsg }}</p>

    <div class="panel reveal reveal-2" style="margin-top: 16px">
      <div class="panel__head">
        <h3>用户列表</h3>
        <span class="hint">{{ users.length }} 条</span>
      </div>
      <div class="panel__body" style="padding: 6px 0">
        <table class="data">
          <thead>
            <tr><th>ID</th><th>用户名</th><th>角色</th><th>状态</th><th>注册时间</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td class="num">{{ u.id }}</td>
              <td style="font-weight: 600">{{ u.username }}</td>
              <td><span :class="['badge', u.role === 'admin' ? 'badge--accent' : '']">{{ u.role }}</span></td>
              <td><span :class="['badge', u.active ? 'badge--ok' : 'badge--danger']"><span class="dot"></span>{{ u.active ? '正常' : '禁用' }}</span></td>
              <td class="num">{{ u.created_at?.slice(0, 10) }}</td>
              <td>
                <div style="display: flex; gap: 6px">
                  <button class="btn btn--ghost btn--sm" @click="showDetail(u)">详情</button>
                  <button class="btn btn--ghost btn--sm" @click="toggleStatus(u)">{{ u.active ? '禁用' : '启用' }}</button>
                  <button class="btn btn--ghost btn--sm" @click="resetPwd(u)">重置密码</button>
                  <button class="btn btn--danger btn--sm" @click="remove(u)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="detail" class="panel panel--accent reveal reveal-3" style="margin-top: 16px">
      <div class="panel__head">
        <h3>用户详情 · {{ detail.username }}</h3>
        <button class="btn btn--ghost btn--sm" @click="detail = null">关闭</button>
      </div>
      <div class="panel__body">
        <div style="display: flex; flex-wrap: wrap; gap: 40px">
          <div><span class="muted">角色</span><div>{{ detail.role }}</div></div>
          <div><span class="muted">状态</span><div>{{ detail.active ? '正常' : '禁用' }}</div></div>
          <div><span class="muted">注册时间</span><div class="mono">{{ detail.created_at }}</div></div>
        </div>
        <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--line)">
          <p class="mono" style="font-size: 0.7rem; letter-spacing: 0.12em; color: var(--text-faint); margin-bottom: 10px">画像</p>
          <div style="display: flex; flex-wrap: wrap; gap: 28px">
            <div><span class="muted">目标</span><div>{{ detail.profile?.goal || '—' }}</div></div>
            <div><span class="muted">年龄</span><div>{{ detail.profile?.age || '—' }}</div></div>
            <div><span class="muted">身高</span><div>{{ detail.profile?.height_cm || '—' }} cm</div></div>
            <div><span class="muted">体重</span><div>{{ detail.profile?.weight_kg || '—' }} kg</div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
