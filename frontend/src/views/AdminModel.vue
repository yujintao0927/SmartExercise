<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const model = ref(null)

const LABELS = {
  target_goal: '训练目标',
  weekly_frequency: '每周频率',
  session_duration_min: '单次时长',
  intensity_level: '训练强度',
  training_cycle_weeks: '训练周期',
}

async function load() {
  const { data } = await api.get('/admin/model')
  model.value = data
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Model</span>
      <h1>模型<em>管理</em></h1>
      <p>推荐模型加载状态、超参数与评估指标。</p>
    </div>

    <div class="panel panel--accent reveal reveal-1">
      <div class="panel__head">
        <h3>模型状态</h3>
        <span class="badge badge--ok"><span class="dot"></span>{{ model?.loaded ? '已加载' : '未加载' }}</span>
      </div>
      <div class="panel__body">
        <div style="display: flex; flex-wrap: wrap; gap: 40px">
          <div>
            <span class="muted">算法</span>
            <div style="font-weight: 600">随机森林 (Random Forest)</div>
          </div>
          <div>
            <span class="muted">最优 n_estimators</span>
            <div class="mono">{{ model?.best_params?.n_estimators }}</div>
          </div>
          <div>
            <span class="muted">最优 max_depth</span>
            <div class="mono">{{ model?.best_params?.max_depth }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="panel reveal reveal-2" style="margin-top: 16px">
      <div class="panel__head">
        <h3>评估指标</h3>
        <span class="hint">测试集</span>
      </div>
      <div class="panel__body" style="padding: 6px 0">
        <table class="data">
          <thead><tr><th>输出</th><th>准确率</th><th>加权 F1</th></tr></thead>
          <tbody>
            <tr v-for="(v, k) in model?.metrics" :key="k">
              <td style="font-weight: 600">{{ LABELS[k] || k }}</td>
              <td class="num">{{ v.accuracy?.toFixed(4) }}</td>
              <td class="num">{{ v.f1?.toFixed(4) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
