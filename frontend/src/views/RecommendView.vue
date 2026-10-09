<script setup>
import { ref } from 'vue'
import api from '../api'

const result = ref(null)
const error = ref('')
const loading = ref(false)

async function generate() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/recommend', {})
    result.value = data
  } catch (e) {
    const d = e.response?.data?.detail
    error.value = Array.isArray(d) ? d[0]?.msg : d || '生成失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="fade-up">
    <span class="tag">Recommend</span>
    <h1 class="title">你的<span class="accent">训练计划</span></h1>

    <button class="btn gen" @click="generate" :disabled="loading">
      {{ loading ? '生成中…' : '生成推荐' }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="result" class="result">
      <div class="stats">
        <div class="card stat">
          <div class="stat__num">{{ result.weekly_frequency }}</div>
          <div class="muted">每周次数</div>
        </div>
        <div class="card stat">
          <div class="stat__num">{{ result.session_duration_min }}<small>min</small></div>
          <div class="muted">单次时长</div>
        </div>
        <div class="card stat">
          <div class="stat__num">{{ result.training_cycle_weeks }}<small>周</small></div>
          <div class="muted">训练周期</div>
        </div>
      </div>

      <div class="card block">
        <div class="row">
          <span class="muted">训练目标</span>
          <span class="tag">{{ result.target_goal }}</span>
        </div>
        <div class="row">
          <span class="muted">强度等级</span>
          <span class="tag">{{ result.intensity_level }}</span>
        </div>
      </div>

      <div class="card block">
        <h3>动作组合</h3>
        <ul class="ex-list">
          <li v-for="(ex, i) in result.exercise_plan" :key="i" class="ex">
            <span class="ex__idx">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="ex__name">{{ ex.name }}</span>
            <span class="ex__meta">{{ ex.sets }} 组 × {{ ex.reps }} 次</span>
          </li>
        </ul>
      </div>

      <p class="muted version">模型版本：{{ result.model_version }}</p>
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

.gen {
  margin-bottom: 16px;
}

.error {
  color: var(--danger);
  margin-bottom: 16px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat {
  padding: 24px;
}

.stat__num {
  font-family: var(--font-display);
  font-size: 3.2rem;
  line-height: 1;
  color: var(--accent);
}

.stat__num small {
  font-size: 1.2rem;
  margin-left: 2px;
  color: var(--text-muted);
}

.block {
  padding: 20px;
  margin-bottom: 16px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--line);
}

.row:last-child {
  border-bottom: none;
}

.block h3 {
  font-size: 1.1rem;
  margin-bottom: 12px;
}

.ex-list {
  list-style: none;
}

.ex {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.ex:last-child {
  border-bottom: none;
}

.ex__idx {
  font-family: var(--font-display);
  color: var(--accent);
  font-size: 1.1rem;
  min-width: 28px;
}

.ex__name {
  flex: 1;
  font-weight: 600;
}

.ex__meta {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.version {
  font-size: 0.85rem;
}
</style>
