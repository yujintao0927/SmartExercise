<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const templates = ref([])
const exercises = ref([])
const goalFilter = ref('')

const GOALS = ['减脂', '增肌', '塑形', '提升耐力', '保持健康']
const INTENSITY = ['低', '中', '高']

const form = ref({
  goal: '增肌', intensity_level: '中', sets: 4, reps: 8,
  session_duration_min: 60, weekly_frequency: 4, training_cycle_weeks: 8, exercise_ids: [],
})
const editingId = ref(null)

async function loadExercises() {
  const { data } = await api.get('/admin/exercises')
  exercises.value = data
}

async function load() {
  const params = {}
  if (goalFilter.value) params.goal = goalFilter.value
  const { data } = await api.get('/admin/templates', { params })
  templates.value = data
}

function toggleExercise(id) {
  const i = form.value.exercise_ids.indexOf(id)
  if (i >= 0) form.value.exercise_ids.splice(i, 1)
  else form.value.exercise_ids.push(id)
}

function startEdit(t) {
  editingId.value = t.id
  form.value = { ...t, exercise_ids: [...(t.exercise_ids || [])] }
}

function resetForm() {
  editingId.value = null
  form.value = { goal: '增肌', intensity_level: '中', sets: 4, reps: 8, session_duration_min: 60, weekly_frequency: 4, training_cycle_weeks: 8, exercise_ids: [] }
}

async function save() {
  if (editingId.value) await api.put(`/admin/templates/${editingId.value}`, form.value)
  else await api.post('/admin/templates', form.value)
  resetForm()
  await load()
}

async function remove(t) {
  if (!confirm(`确定删除模板「${t.goal}·${t.intensity_level}」？`)) return
  await api.delete(`/admin/templates/${t.id}`)
  await load()
}

function exName(id) {
  return exercises.value.find((e) => e.id === id)?.name || id
}

onMounted(() => { loadExercises(); load() })
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Templates</span>
      <h1>计划<em>模板</em></h1>
      <p>维护目标 × 强度的计划模板，供推荐组装动作组合。</p>
    </div>

    <form class="panel panel--accent reveal reveal-1" style="padding: 24px" @submit.prevent="save">
      <h3 style="font-size: 1rem; margin-bottom: 16px">{{ editingId ? `编辑模板 #${editingId}` : '新增模板' }}</h3>
      <div class="form-grid">
        <div class="field">
          <label>目标</label>
          <select v-model="form.goal"><option v-for="g in GOALS" :key="g" :value="g">{{ g }}</option></select>
        </div>
        <div class="field">
          <label>强度</label>
          <select v-model="form.intensity_level"><option v-for="i in INTENSITY" :key="i" :value="i">{{ i }}</option></select>
        </div>
        <div class="field">
          <label>组数</label>
          <input v-model.number="form.sets" type="number" min="1" />
        </div>
        <div class="field">
          <label>次数</label>
          <input v-model.number="form.reps" type="number" min="1" />
        </div>
        <div class="field">
          <label>单次时长 (分)</label>
          <input v-model.number="form.session_duration_min" type="number" min="10" />
        </div>
        <div class="field">
          <label>每周频率</label>
          <input v-model.number="form.weekly_frequency" type="number" min="1" max="7" />
        </div>
        <div class="field">
          <label>周期 (周)</label>
          <input v-model.number="form.training_cycle_weeks" type="number" min="1" />
        </div>
      </div>

      <div class="field">
        <label>动作组合（{{ form.exercise_ids.length }} 个）</label>
        <div style="display: flex; flex-wrap: wrap; gap: 8px">
          <button
            v-for="e in exercises"
            :key="e.id"
            type="button"
            class="chip"
            :class="{ 'chip--on': form.exercise_ids.includes(e.id) }"
            @click="toggleExercise(e.id)"
          >{{ e.name }}</button>
        </div>
      </div>

      <div style="display: flex; gap: 8px">
        <button class="btn" type="submit">{{ editingId ? '保存修改' : '新增模板' }}</button>
        <button v-if="editingId" class="btn btn--ghost" type="button" @click="resetForm">取消</button>
      </div>
    </form>

    <div class="panel reveal reveal-2" style="margin-top: 16px">
      <div class="panel__head">
        <h3>模板列表</h3>
        <select v-model="goalFilter" style="background: var(--bg); border: 1px solid var(--line-strong); color: var(--text); border-radius: 6px; padding: 6px 10px; font-size: 0.85rem" @change="load">
          <option value="">全部目标</option>
          <option v-for="g in GOALS" :key="g" :value="g">{{ g }}</option>
        </select>
      </div>
      <div class="panel__body" style="padding: 6px 0">
        <div v-if="!templates.length" class="empty"><div class="glyph">—</div><p>暂无模板</p></div>
        <table v-else class="data">
          <thead><tr><th>目标</th><th>强度</th><th>动作</th><th>组 × 次</th><th>频率</th><th>周期</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="t in templates" :key="t.id">
              <td><span class="badge badge--accent">{{ t.goal }}</span></td>
              <td>{{ t.intensity_level }}</td>
              <td class="muted" style="font-size: 0.85rem">{{ t.exercise_ids.map(exName).join('、') }}</td>
              <td class="num">{{ t.sets }} × {{ t.reps }}</td>
              <td class="num">{{ t.weekly_frequency }} 次/周</td>
              <td class="num">{{ t.training_cycle_weeks }} 周</td>
              <td>
                <div style="display: flex; gap: 6px">
                  <button class="btn btn--ghost btn--sm" @click="startEdit(t)">编辑</button>
                  <button class="btn btn--danger btn--sm" @click="remove(t)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chip {
  background: var(--bg);
  border: 1px solid var(--line-strong);
  border-radius: 999px;
  color: var(--text-muted);
  padding: 7px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.15s var(--ease);
}
.chip:hover { border-color: var(--text-faint); color: var(--text); }
.chip--on { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
</style>
