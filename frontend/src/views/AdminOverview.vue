<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const overview = ref(null)
const growthEl = ref(null)
const goalEl = ref(null)
const completionEl = ref(null)

const PALETTE = ['#ffb300', '#37e0a0', '#4d9fff', '#ff4d5e', '#c8ff00']

function baseChart(el, option) {
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption({ backgroundColor: 'transparent', ...option })
}

function drawGrowth() {
  const g = overview.value.user_growth
  baseChart(growthEl.value, {
    grid: { left: 40, right: 16, top: 30, bottom: 28 },
    xAxis: { type: 'category', data: g.map((x) => x.date), axisLine: { lineStyle: { color: '#34343d' } }, axisLabel: { color: '#8a8a92' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#26262e' } }, axisLabel: { color: '#8a8a92' } },
    tooltip: { trigger: 'axis', backgroundColor: '#18181e', borderColor: '#34343d', textStyle: { color: '#f2f2ee' } },
    series: [{ type: 'line', data: g.map((x) => x.count), smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: { color: '#ffb300', width: 2 }, itemStyle: { color: '#ffb300' }, areaStyle: { color: 'rgba(255,179,0,0.08)' } }],
  })
}

function drawGoal() {
  const g = overview.value.goal_distribution
  baseChart(goalEl.value, {
    grid: { left: 90, right: 20, top: 10, bottom: 28 },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#26262e' } }, axisLabel: { color: '#8a8a92' } },
    yAxis: { type: 'category', data: g.map((x) => x.goal), axisLine: { lineStyle: { color: '#34343d' } }, axisLabel: { color: '#c9c9cf' } },
    tooltip: { trigger: 'axis', backgroundColor: '#18181e', borderColor: '#34343d', textStyle: { color: '#f2f2ee' } },
    series: [{ type: 'bar', data: g.map((x) => x.count), barWidth: 14, itemStyle: { color: '#ffb300', borderRadius: [0, 4, 4, 0] } }],
  })
}

function drawCompletion() {
  const c = overview.value.completion_distribution
  baseChart(completionEl.value, {
    grid: { left: 50, right: 20, top: 30, bottom: 28 },
    xAxis: { type: 'category', data: c.map((x) => x.range), axisLine: { lineStyle: { color: '#34343d' } }, axisLabel: { color: '#8a8a92' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#26262e' } }, axisLabel: { color: '#8a8a92' } },
    tooltip: { trigger: 'axis', backgroundColor: '#18181e', borderColor: '#34343d', textStyle: { color: '#f2f2ee' } },
    series: [{ type: 'bar', data: c.map((x) => x.count), barWidth: 28, itemStyle: { color: '#37e0a0', borderRadius: [4, 4, 0, 0] } }],
  })
}

async function load() {
  const { data } = await api.get('/admin/overview')
  overview.value = data
  drawGrowth()
  drawGoal()
  drawCompletion()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Overview</span>
      <h1>数据<em>总览</em></h1>
      <p>系统运行概况与关键指标。</p>
    </div>

    <div class="kpi-grid reveal reveal-1">
      <div class="kpi"><div class="kpi__label">累计用户</div><div class="kpi__value">{{ overview?.kpi.total_users }}</div></div>
      <div class="kpi"><div class="kpi__label">今日新增</div><div class="kpi__value">{{ overview?.kpi.new_users_today }}<em> 人</em></div></div>
      <div class="kpi"><div class="kpi__label">累计推荐</div><div class="kpi__value">{{ overview?.kpi.total_recommendations }}</div></div>
      <div class="kpi"><div class="kpi__label">累计打卡</div><div class="kpi__value">{{ overview?.kpi.total_sessions }}</div></div>
      <div class="kpi"><div class="kpi__label">本周活跃</div><div class="kpi__value">{{ overview?.kpi.active_users_week }}<em> 人</em></div></div>
    </div>

    <div style="display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; margin-top: 16px">
      <div class="panel reveal reveal-2">
        <div class="panel__head"><h3>用户增长趋势</h3><span class="hint">近 20 天</span></div>
        <div class="panel__body"><div ref="growthEl" class="chart"></div></div>
      </div>
      <div class="panel reveal reveal-2">
        <div class="panel__head"><h3>训练目标分布</h3></div>
        <div class="panel__body"><div ref="goalEl" class="chart"></div></div>
      </div>
    </div>

    <div class="panel reveal reveal-3" style="margin-top: 16px">
      <div class="panel__head"><h3>完成率分布</h3></div>
      <div class="panel__body"><div ref="completionEl" class="chart"></div></div>
    </div>
  </div>
</template>

<style scoped>
@media (max-width: 900px) {
  .panel__body { padding: 16px; }
}
</style>
