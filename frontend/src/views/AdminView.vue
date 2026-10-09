<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const users = ref([])
const model = ref(null)
const error = ref('')

async function load() {
  try {
    const [u, m] = await Promise.all([
      api.get('/admin/users'),
      api.get('/admin/model'),
    ])
    users.value = u.data
    model.value = m.data
  } catch (e) {
    error.value = e.response?.status === 403 ? '无管理员权限' : '加载失败'
  }
}

onMounted(load)
</script>

<template>
  <div class="fade-up">
    <span class="tag">Admin</span>
    <h1 class="title">管理<span class="accent">面板</span></h1>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="model" class="card block">
      <h3>模型信息</h3>
      <div class="row"><span class="muted">最优超参</span><span>{{ JSON.stringify(model.best_params) }}</span></div>
      <div class="row">
        <span class="muted">加权 F1</span>
        <span>{{ model.metrics?.target_goal?.f1?.toFixed(4) }}</span>
      </div>
    </div>

    <div class="card block">
      <h3>用户列表（{{ users.length }}）</h3>
      <ul class="list">
        <li v-for="u in users" :key="u.id" class="row">
          <span>{{ u.username }}</span>
          <span class="tag">{{ u.role }}</span>
          <span class="muted">{{ u.created_at }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.title {
  font-size: clamp(2rem, 5vw, 3.4rem);
  margin: 8px 0 20px;
}

.accent {
  color: var(--accent);
}

.block {
  padding: 20px;
  margin-bottom: 16px;
}

.block h3 {
  font-size: 1.1rem;
  margin-bottom: 12px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--line);
}

.list {
  list-style: none;
}

.error {
  color: var(--danger);
  margin-bottom: 12px;
}
</style>
