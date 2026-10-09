<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const stat = ref(null)

async function load() {
  const { data } = await api.get('/admin/training')
  stat.value = data
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Training</span>
      <h1>训练<em>数据</em></h1>
      <p>全站训练打卡统计。</p>
    </div>

    <div class="kpi-grid reveal reveal-1">
      <div class="kpi"><div class="kpi__label">累计打卡</div><div class="kpi__value">{{ stat?.total_sessions }}</div></div>
      <div class="kpi"><div class="kpi__label">平均完成率</div><div class="kpi__value">{{ stat ? Math.round(stat.avg_completion * 100) : '—' }}<em>%</em></div></div>
      <div class="kpi"><div class="kpi__label">平均疲劳</div><div class="kpi__value">{{ stat?.avg_fatigue }}<em>/10</em></div></div>
    </div>

    <div class="panel reveal reveal-2" style="margin-top: 16px">
      <div class="panel__head"><h3>完成率分布</h3></div>
      <div class="panel__body" style="padding: 6px 0">
        <table class="data">
          <thead><tr><th>区间</th><th>人次</th><th>占比</th></tr></thead>
          <tbody>
            <tr v-for="c in stat?.completion_distribution" :key="c.range">
              <td style="font-weight: 600">{{ c.range }}</td>
              <td class="num">{{ c.count }}</td>
              <td class="num">{{ Math.round((c.count / (stat?.total_sessions || 1)) * 100) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
