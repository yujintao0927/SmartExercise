<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const plan = ref(null)
const error = ref('')
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    const { data } = await api.post('/recommend', {})
    plan.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || '请先录入画像'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Plan</span>
      <h1>当前<em>训练计划</em></h1>
      <p>系统根据你的画像生成的生效计划。</p>
    </div>

    <div v-if="loading" class="empty"><div class="glyph">…</div><p>加载中</p></div>
    <p v-else-if="error" class="error-text">{{ error }}</p>

    <template v-else-if="plan">
      <div class="panel panel--accent reveal reveal-1">
        <div class="panel__head">
          <h3>计划概览</h3>
          <span class="badge badge--accent">{{ plan.target_goal }}</span>
        </div>
        <div class="panel__body">
          <div class="kpi-grid">
            <div class="kpi">
              <div class="kpi__label">每周频率</div>
              <div class="kpi__value">{{ plan.weekly_frequency }}<em> 次</em></div>
            </div>
            <div class="kpi">
              <div class="kpi__label">单次时长</div>
              <div class="kpi__value">{{ plan.session_duration_min }}<em> 分</em></div>
            </div>
            <div class="kpi">
              <div class="kpi__label">训练周期</div>
              <div class="kpi__value">{{ plan.training_cycle_weeks }}<em> 周</em></div>
            </div>
            <div class="kpi">
              <div class="kpi__label">强度等级</div>
              <div class="kpi__value">{{ plan.intensity_level }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel reveal reveal-2" style="margin-top: 16px">
        <div class="panel__head">
          <h3>动作组合</h3>
          <span class="hint">{{ plan.exercise_plan.length }} 个动作</span>
        </div>
        <div class="panel__body" style="padding: 6px 0">
          <table class="data">
            <thead>
              <tr><th>#</th><th>动作</th><th>组数</th><th>次数</th></tr>
            </thead>
            <tbody>
              <tr v-for="(ex, i) in plan.exercise_plan" :key="i">
                <td class="num">{{ String(i + 1).padStart(2, '0') }}</td>
                <td style="font-weight: 600">{{ ex.name }}</td>
                <td class="num">{{ ex.sets }}</td>
                <td class="num">{{ ex.reps }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="panel reveal reveal-3" style="margin-top: 16px">
        <div class="panel__head">
          <h3>周期进度</h3>
          <span class="hint">第 4 / {{ plan.training_cycle_weeks }} 周</span>
        </div>
        <div class="panel__body">
          <div style="height: 8px; background: var(--bg); border-radius: 999px; overflow: hidden">
            <div style="height: 100%; width: 50%; background: var(--accent); border-radius: 999px"></div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
