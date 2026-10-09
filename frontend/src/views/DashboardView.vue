<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const trainingEl = ref(null)
const weightEl = ref(null)

function draw(el, xData, yData, name, color) {
  if (!el) return
  const chart = echarts.init(el)
  chart.setOption({
    backgroundColor: 'transparent',
    grid: { left: 44, right: 20, top: 30, bottom: 28 },
    xAxis: {
      type: 'category',
      data: xData,
      axisLine: { lineStyle: { color: '#34343d' } },
      axisLabel: { color: '#8a8a92', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#26262e' } },
      axisLabel: { color: '#8a8a92', fontSize: 11 },
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#18181e',
      borderColor: '#34343d',
      textStyle: { color: '#f2f2ee' },
    },
    series: [{
      name,
      type: 'line',
      data: yData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color, width: 2 },
      itemStyle: { color },
      areaStyle: { color: 'rgba(200,255,0,0.07)' },
    }],
  })
}

async function load() {
  const { data } = await api.get('/dashboard/summary')
  draw(trainingEl.value, data.training.map((r) => r.date), data.training.map((r) => Math.round(r.completion_rate * 100)), '完成率 %', '#c8ff00')
  draw(weightEl.value, data.weight.map((r) => r.date), data.weight.map((r) => r.weight_kg), '体重 kg', '#37e0a0')
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Dashboard</span>
      <h1>效果<em>可视化</em></h1>
      <p>训练完成率与体重变化趋势。</p>
    </div>

    <div class="panel reveal reveal-1">
      <div class="panel__head">
        <h3>训练完成率趋势</h3>
        <span class="hint">%</span>
      </div>
      <div class="panel__body"><div ref="trainingEl" class="chart"></div></div>
    </div>

    <div class="panel reveal reveal-2" style="margin-top: 16px">
      <div class="panel__head">
        <h3>体重变化趋势</h3>
        <span class="hint">kg</span>
      </div>
      <div class="panel__body"><div ref="weightEl" class="chart"></div></div>
    </div>
  </div>
</template>
