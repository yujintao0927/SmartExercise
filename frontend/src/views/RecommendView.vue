<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const result = ref(null)
const history = ref([])
const error = ref('')
const loading = ref(false)

async function loadHistory() {
  try {
    const { data } = await api.get('/recommend/history')
    history.value = data
  } catch { /* ignore */ }
}

async function generate() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/recommend', {})
    result.value = data
    await loadHistory()
  } catch (e) {
    const d = e.response?.data?.detail
    error.value = Array.isArray(d) ? d[0]?.msg : d || '生成失败，请先录入画像'
  } finally {
    loading.value = false
  }
}

function fmtTime(s) {
  return s ? s.replace('T', ' ').slice(0, 16) : ''
}

onMounted(loadHistory)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Recommend</span>
      <h1>智能<em>推荐</em></h1>
      <p>基于随机森林模型，生成 6 类结构化训练结果。</p>
    </div>

    <button class="btn reveal reveal-1" @click="generate" :disabled="loading">
      {{ loading ? '生成中…' : '生成推荐' }}
    </button>
    <p v-if="error" class="error-text" style="margin-top: 12px">{{ error }}</p>

    <template v-if="result">
      <div class="panel panel--accent reveal reveal-2" style="margin-top: 20px">
        <div class="panel__head">
          <h3>推荐结果</h3>
          <div style="display: flex; gap: 8px">
            <span class="badge badge--accent">{{ result.target_goal }}</span>
            <span class="badge">{{ result.intensity_level }} 强度</span>
          </div>
        </div>
        <div class="panel__body">
          <div class="kpi-grid">
            <div class="kpi">
              <div class="kpi__label">每周频率</div>
              <div class="kpi__value">{{ result.weekly_frequency }}<em> 次</em></div>
            </div>
            <div class="kpi">
              <div class="kpi__label">单次时长</div>
              <div class="kpi__value">{{ result.session_duration_min }}<em> 分</em></div>
            </div>
            <div class="kpi">
              <div class="kpi__label">训练周期</div>
              <div class="kpi__value">{{ result.training_cycle_weeks }}<em> 周</em></div>
            </div>
          </div>

          <div style="margin-top: 20px">
            <h4 style="font-size: 0.8rem; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 8px">动作组合</h4>
            <div style="display: flex; flex-direction: column">
              <div
                v-for="(ex, i) in result.exercise_plan"
                :key="i"
                style="display: flex; align-items: center; gap: 14px; padding: 12px 0; border-bottom: 1px solid var(--line)"
              >
                <span class="mono" style="color: var(--accent)">{{ String(i + 1).padStart(2, '0') }}</span>
                <span style="flex: 1; font-weight: 600">{{ ex.name }}</span>
                <span class="muted" style="font-size: 0.88rem">{{ ex.sets }} 组 × {{ ex.reps }} 次</span>
              </div>
            </div>
          </div>

          <p class="mono" style="font-size: 0.72rem; color: var(--text-faint); margin-top: 16px">模型版本 {{ result.model_version }}</p>
        </div>
      </div>
    </template>

    <div class="panel reveal reveal-3" style="margin-top: 20px">
      <div class="panel__head">
        <h3>推荐历史</h3>
        <span class="hint">{{ history.length }} 条</span>
      </div>
      <div class="panel__body" style="padding: 6px 0">
        <div v-if="!history.length" class="empty"><div class="glyph">—</div><p>暂无推荐记录</p></div>
        <table v-else class="data">
          <thead>
            <tr><th>时间</th><th>目标</th><th>频率</th><th>强度</th><th>周期</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in history" :key="r.id">
              <td class="num">{{ fmtTime(r.created_at) }}</td>
              <td style="font-weight: 600">{{ r.target_goal }}</td>
              <td class="num">{{ r.weekly_frequency }} 次/周</td>
              <td>{{ r.intensity_level }}</td>
              <td class="num">{{ r.training_cycle_weeks }} 周</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
