<script setup>
import { onMounted, ref, computed } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const profile = ref(null)
const stats = ref(null)
const summary = ref(null)

const latestWeight = computed(() => summary.value?.weight?.at(-1)?.weight_kg)

async function load() {
  const [p, s, d] = await Promise.all([
    api.get('/profile'),
    api.get('/training/stats'),
    api.get('/dashboard/summary'),
  ])
  profile.value = p.data
  stats.value = s.data
  summary.value = d.data
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Overview</span>
      <h1>继续，<em>{{ auth.displayName }}</em></h1>
      <p v-if="profile">目标「{{ profile.goal }}」· 保持节奏，今天也要训练。</p>
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
        <div class="kpi__label">本周完成率</div>
        <div class="kpi__value">{{ stats ? Math.round(stats.week_completion_avg * 100) : '—' }}<em>%</em></div>
      </div>
      <div class="kpi">
        <div class="kpi__label">当前体重</div>
        <div class="kpi__value">{{ latestWeight ?? '—' }}<em> kg</em></div>
      </div>
    </div>

    <div class="panel panel--accent reveal reveal-2" style="margin-top: 22px">
      <div class="panel__head">
        <h3>今日训练计划</h3>
        <span class="hint">基于最新推荐</span>
      </div>
      <div class="panel__body">
        <div style="display: flex; flex-wrap: wrap; gap: 24px">
          <div><span class="muted">训练目标</span><div style="font-size: 1.1rem; font-weight: 600">{{ profile?.goal || '—' }}</div></div>
          <div><span class="muted">每周频率</span><div style="font-size: 1.1rem; font-weight: 600">4 次 / 周</div></div>
          <div><span class="muted">单次时长</span><div style="font-size: 1.1rem; font-weight: 600">60 分钟</div></div>
          <div><span class="muted">强度等级</span><div style="font-size: 1.1rem; font-weight: 600">中</div></div>
        </div>
      </div>
    </div>

    <div class="panel reveal reveal-3" style="margin-top: 16px">
      <div class="panel__head">
        <h3>快捷操作</h3>
      </div>
      <div class="panel__body">
        <div style="display: flex; flex-wrap: wrap; gap: 10px">
          <router-link to="/recommend" class="btn">生成推荐</router-link>
          <router-link to="/training" class="btn btn--ghost">训练打卡</router-link>
          <router-link to="/body" class="btn btn--ghost">记录体重</router-link>
          <router-link to="/plan" class="btn btn--ghost">查看计划</router-link>
        </div>
      </div>
    </div>
  </div>
</template>
