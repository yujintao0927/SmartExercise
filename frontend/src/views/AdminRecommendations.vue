<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const items = ref([])

async function load() {
  const { data } = await api.get('/admin/recommendations')
  items.value = data.items
}

function fmtTime(s) {
  return s ? s.replace('T', ' ').slice(0, 16) : ''
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Recommendations</span>
      <h1>推荐<em>记录</em></h1>
      <p>全站推荐生成记录。</p>
    </div>

    <div class="panel reveal reveal-1">
      <div class="panel__head">
        <h3>推荐记录</h3>
        <span class="hint">{{ items.length }} 条</span>
      </div>
      <div class="panel__body" style="padding: 6px 0">
        <div v-if="!items.length" class="empty"><div class="glyph">—</div><p>暂无记录</p></div>
        <table v-else class="data">
          <thead>
            <tr><th>ID</th><th>用户</th><th>目标</th><th>强度</th><th>生成时间</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in items" :key="r.id">
              <td class="num">{{ r.id }}</td>
              <td style="font-weight: 600">{{ r.username }}</td>
              <td><span class="badge badge--accent">{{ r.target_goal }}</span></td>
              <td>{{ r.intensity_level }}</td>
              <td class="num">{{ fmtTime(r.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
