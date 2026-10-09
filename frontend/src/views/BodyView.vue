<script setup>
import { onMounted, ref, computed } from 'vue'
import api from '../api'

const form = ref({ record_date: new Date().toISOString().slice(0, 10), weight_kg: 70 })
const records = ref([])
const error = ref('')

const latest = computed(() => records.value[0])
const prev = computed(() => records.value[1])

async function load() {
  try {
    const { data } = await api.get('/metrics/weight')
    records.value = data
  } catch { /* ignore */ }
}

async function submit() {
  error.value = ''
  try {
    await api.post('/metrics/weight', form.value)
    await load()
  } catch (e) {
    const d = e.response?.data?.detail
    error.value = Array.isArray(d) ? d[0]?.msg : d || '记录失败'
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Body</span>
      <h1>身体<em>数据</em></h1>
      <p>记录体重，系统按身高自动计算 BMI。</p>
    </div>

    <div class="kpi-grid reveal reveal-1">
      <div class="kpi">
        <div class="kpi__label">当前体重</div>
        <div class="kpi__value">{{ latest?.weight_kg ?? '—' }}<em> kg</em></div>
        <div v-if="latest && prev" class="kpi__delta">较上次 {{ (latest.weight_kg - prev.weight_kg).toFixed(1) }} kg</div>
      </div>
      <div class="kpi">
        <div class="kpi__label">当前 BMI</div>
        <div class="kpi__value">{{ latest?.bmi ?? '—' }}</div>
      </div>
      <div class="kpi">
        <div class="kpi__label">记录次数</div>
        <div class="kpi__value">{{ records.length }}<em> 次</em></div>
      </div>
    </div>

    <form class="panel panel--accent reveal reveal-2" style="margin-top: 16px; padding: 24px" @submit.prevent="submit">
      <div class="form-grid">
        <div class="field">
          <label>记录日期</label>
          <input v-model="form.record_date" type="date" required />
        </div>
        <div class="field">
          <label>体重 (kg)</label>
          <input v-model.number="form.weight_kg" type="number" min="30" max="250" step="0.1" required />
        </div>
      </div>
      <p v-if="error" class="error-text" style="margin-bottom: 14px">{{ error }}</p>
      <button class="btn" type="submit">记录体重</button>
    </form>

    <div class="panel reveal reveal-3" style="margin-top: 16px">
      <div class="panel__head">
        <h3>体重历史</h3>
        <span class="hint">{{ records.length }} 条</span>
      </div>
      <div class="panel__body" style="padding: 6px 0">
        <div v-if="!records.length" class="empty"><div class="glyph">—</div><p>暂无体重记录</p></div>
        <table v-else class="data">
          <thead>
            <tr><th>日期</th><th>体重</th><th>BMI</th><th>变化</th></tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in records" :key="r.id">
              <td class="num">{{ r.record_date }}</td>
              <td class="num">{{ r.weight_kg }} kg</td>
              <td class="num">{{ r.bmi ?? '—' }}</td>
              <td class="num" :style="{ color: i + 1 < records.length ? (r.weight_kg > records[i + 1].weight_kg ? 'var(--ok)' : 'var(--danger)') : 'var(--text-faint)' }">
                {{ i + 1 < records.length ? (r.weight_kg - records[i + 1].weight_kg).toFixed(1) + ' kg' : '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
