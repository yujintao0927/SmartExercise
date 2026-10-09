<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const form = ref({
  train_date: new Date().toISOString().slice(0, 10),
  completion_rate: 1,
  fatigue_score: 5,
  feedback: '适中',
  duration_min: 60,
})

const records = ref([])
const adjustment = ref(null)
const error = ref('')

async function load() {
  const { data } = await api.get('/dashboard/summary')
  records.value = data.training
  adjustment.value = data.adjustment
}

async function submit() {
  error.value = ''
  try {
    await api.post('/training/records', form.value)
    await load()
  } catch (e) {
    const d = e.response?.data?.detail
    error.value = Array.isArray(d) ? d[0]?.msg : d || '打卡失败'
  }
}

onMounted(load)
</script>

<template>
  <div class="fade-up">
    <span class="tag">Training</span>
    <h1 class="title">训练<span class="accent">打卡</span></h1>

    <div v-if="adjustment?.available" class="card adjust">
      <h3>动态调整建议</h3>
      <p>{{ adjustment.advice }}</p>
    </div>

    <form class="card form" @submit.prevent="submit">
      <div class="grid">
        <div class="field">
          <label>训练日期</label>
          <input v-model="form.train_date" type="date" required />
        </div>
        <div class="field">
          <label>完成率（{{ Math.round(form.completion_rate * 100) }}%）</label>
          <input v-model.number="form.completion_rate" type="range" min="0" max="1" step="0.1" />
        </div>
        <div class="field">
          <label>疲劳评分（{{ form.fatigue_score }}/10）</label>
          <input v-model.number="form.fatigue_score" type="range" min="1" max="10" />
        </div>
        <div class="field">
          <label>反馈</label>
          <select v-model="form.feedback">
            <option>太轻松</option>
            <option>适中</option>
            <option>太累</option>
          </select>
        </div>
        <div class="field">
          <label>实际时长 (分钟)</label>
          <input v-model.number="form.duration_min" type="number" min="0" />
        </div>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="btn" type="submit">提交打卡</button>
    </form>

    <div class="card block">
      <h3>历史记录</h3>
      <p v-if="!records.length" class="muted">暂无训练记录</p>
      <ul class="list">
        <li v-for="r in records.slice().reverse()" :key="r.date" class="row">
          <span>{{ r.date }}</span>
          <span class="muted">完成率 {{ Math.round(r.completion_rate * 100) }}%</span>
          <span class="muted">疲劳 {{ r.fatigue_score }}</span>
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

.adjust {
  padding: 20px;
  margin-bottom: 16px;
}

.adjust h3 {
  font-size: 1.1rem;
  margin-bottom: 6px;
}

.form {
  padding: 24px;
  margin-bottom: 16px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0 20px;
}

.block {
  padding: 20px;
}

.block h3 {
  font-size: 1.1rem;
  margin-bottom: 12px;
}

.list {
  list-style: none;
}

.row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--line);
}

.error {
  color: var(--danger);
  margin-bottom: 12px;
}
</style>
