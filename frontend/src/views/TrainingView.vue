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
const stats = ref(null)
const adjustment = ref(null)
const error = ref('')

async function load() {
  const [s, d, r] = await Promise.all([
    api.get('/training/stats'),
    api.get('/dashboard/summary'),
    api.get('/training/records'),
  ])
  stats.value = s.data
  adjustment.value = d.data.adjustment
  records.value = r.data
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
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Training</span>
      <h1>训练<em>打卡</em></h1>
      <p>记录每次训练，系统会根据完成率与疲劳动态调整计划。</p>
    </div>

    <div class="kpi-grid reveal reveal-1">
      <div class="kpi">
        <div class="kpi__label">连续打卡</div>
        <div class="kpi__value">{{ stats?.streak_days ?? '—' }}<em> 天</em></div>
      </div>
      <div class="kpi">
        <div class="kpi__label">累计训练</div>
        <div class="kpi__value">{{ stats?.total_sessions ?? '—' }}<em> 次</em></div>
      </div>
      <div class="kpi">
        <div class="kpi__label">本周打卡</div>
        <div class="kpi__value">{{ stats?.week_sessions ?? '—' }}<em> 次</em></div>
      </div>
      <div class="kpi">
        <div class="kpi__label">本周完成率</div>
        <div class="kpi__value">{{ stats ? Math.round(stats.week_completion_avg * 100) : '—' }}<em>%</em></div>
      </div>
    </div>

    <div v-if="adjustment?.available" class="panel reveal reveal-2" style="margin-top: 16px; border-color: var(--accent-dim)">
      <div class="panel__head">
        <h3>动态调整建议</h3>
        <span class="badge badge--accent">AI 建议</span>
      </div>
      <div class="panel__body" style="color: var(--text-muted)">{{ adjustment.advice }}</div>
    </div>

    <form class="panel panel--accent reveal reveal-2" style="margin-top: 16px; padding: 24px" @submit.prevent="submit">
      <div class="form-grid">
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
          <label>主观反馈</label>
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
      <p v-if="error" class="error-text" style="margin-bottom: 14px">{{ error }}</p>
      <button class="btn" type="submit">提交打卡</button>
    </form>

    <div class="panel reveal reveal-3" style="margin-top: 16px">
      <div class="panel__head">
        <h3>打卡历史</h3>
        <span class="hint">{{ records.length }} 条</span>
      </div>
      <div class="panel__body" style="padding: 6px 0">
        <div v-if="!records.length" class="empty"><div class="glyph">—</div><p>暂无训练记录</p></div>
        <table v-else class="data">
          <thead>
            <tr><th>日期</th><th>完成率</th><th>疲劳</th><th>反馈</th><th>时长</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td class="num">{{ r.train_date }}</td>
              <td class="num">{{ Math.round(r.completion_rate * 100) }}%</td>
              <td class="num">{{ r.fatigue_score }}/10</td>
              <td>{{ r.feedback || '—' }}</td>
              <td class="num">{{ r.duration_min ? r.duration_min + ' 分' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
