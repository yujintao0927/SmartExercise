<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const trainingEl = ref(null)
const weightEl = ref(null)
const range = ref('all')

async function load() {
  const { data } = await api.get('/dashboard/summary')
  draw(trainingEl.value, data.training.map((r) => [r.date, r.completion_rate]), '完成率')
  draw(weightEl.value, data.weight.map((r) => [r.date, r.weight_kg]), '体重 (kg)')
}

function draw(el, data, name) {
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption({
    backgroundColor: 'transparent',
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      data: data.map((d) => d[0]),
      axisLine: { lineStyle: { color: '#2b2b31' } },
      axisLabel: { color: '#8f8f96' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#2b2b31' } },
      axisLabel: { color: '#8f8f96' },
    },
    series: [
      {
        name,
        type: 'line',
        data: data.map((d) => d[1]),
        smooth: true,
        lineStyle: { color: '#c8ff00', width: 2 },
        itemStyle: { color: '#c8ff00' },
        areaStyle: { color: 'rgba(200,255,0,0.08)' },
      },
    ],
    tooltip: { trigger: 'axis' },
  })
  return chart
}

onMounted(load)
</script>

<template>
  <div class="fade-up">
    <span class="tag">Dashboard</span>
    <h1 class="title">效果<span class="accent">可视化</span></h1>

    <div class="card block">
      <h3>训练完成率趋势</h3>
      <div ref="trainingEl" class="chart"></div>
    </div>

    <div class="card block">
      <h3>体重变化趋势</h3>
      <div ref="weightEl" class="chart"></div>
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

.chart {
  width: 100%;
  height: 280px;
}
</style>
