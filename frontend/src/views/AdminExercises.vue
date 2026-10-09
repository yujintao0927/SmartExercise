<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const exercises = ref([])
const muscleFilter = ref('')
const typeFilter = ref('')

const MUSCLES = ['背', '腿', '胸', '肩', '核心', '全身']
const TYPES = ['力量', '有氧', '柔韧']

const form = ref({ name: '', muscle_group: '背', exercise_type: '力量' })
const editingId = ref(null)

async function load() {
  const params = {}
  if (muscleFilter.value) params.muscle_group = muscleFilter.value
  if (typeFilter.value) params.exercise_type = typeFilter.value
  const { data } = await api.get('/admin/exercises', { params })
  exercises.value = data
}

function startEdit(ex) {
  editingId.value = ex.id
  form.value = { name: ex.name, muscle_group: ex.muscle_group, exercise_type: ex.exercise_type }
}

function resetForm() {
  editingId.value = null
  form.value = { name: '', muscle_group: '背', exercise_type: '力量' }
}

async function save() {
  if (editingId.value) await api.put(`/admin/exercises/${editingId.value}`, form.value)
  else await api.post('/admin/exercises', form.value)
  resetForm()
  await load()
}

async function remove(ex) {
  if (!confirm(`确定删除动作「${ex.name}」？`)) return
  await api.delete(`/admin/exercises/${ex.id}`)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-head reveal">
      <span class="eyebrow">Exercises</span>
      <h1>动作<em>库</em></h1>
      <p>维护系统动作库，供计划模板引用。</p>
    </div>

    <form class="panel panel--accent reveal reveal-1" style="padding: 24px" @submit.prevent="save">
      <h3 style="font-size: 1rem; margin-bottom: 16px">{{ editingId ? `编辑动作 #${editingId}` : '新增动作' }}</h3>
      <div class="form-grid">
        <div class="field">
          <label>动作名称</label>
          <input v-model="form.name" required placeholder="如 硬拉" />
        </div>
        <div class="field">
          <label>肌肉群</label>
          <select v-model="form.muscle_group">
            <option v-for="m in MUSCLES" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <div class="field">
          <label>类型</label>
          <select v-model="form.exercise_type">
            <option v-for="t in TYPES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </div>
      <div style="display: flex; gap: 8px">
        <button class="btn" type="submit">{{ editingId ? '保存修改' : '新增动作' }}</button>
        <button v-if="editingId" class="btn btn--ghost" type="button" @click="resetForm">取消</button>
      </div>
    </form>

    <div class="panel reveal reveal-2" style="margin-top: 16px">
      <div class="panel__head">
        <h3>动作列表</h3>
        <div style="display: flex; gap: 8px">
          <select v-model="muscleFilter" style="background: var(--bg); border: 1px solid var(--line-strong); color: var(--text); border-radius: 6px; padding: 6px 10px; font-size: 0.85rem" @change="load">
            <option value="">全部肌肉群</option>
            <option v-for="m in MUSCLES" :key="m" :value="m">{{ m }}</option>
          </select>
          <select v-model="typeFilter" style="background: var(--bg); border: 1px solid var(--line-strong); color: var(--text); border-radius: 6px; padding: 6px 10px; font-size: 0.85rem" @change="load">
            <option value="">全部类型</option>
            <option v-for="t in TYPES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </div>
      <div class="panel__body" style="padding: 6px 0">
        <div v-if="!exercises.length" class="empty"><div class="glyph">—</div><p>暂无动作</p></div>
        <table v-else class="data">
          <thead><tr><th>ID</th><th>动作</th><th>肌肉群</th><th>类型</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="ex in exercises" :key="ex.id">
              <td class="num">{{ ex.id }}</td>
              <td style="font-weight: 600">{{ ex.name }}</td>
              <td><span class="badge">{{ ex.muscle_group }}</span></td>
              <td><span class="badge">{{ ex.exercise_type }}</span></td>
              <td>
                <div style="display: flex; gap: 6px">
                  <button class="btn btn--ghost btn--sm" @click="startEdit(ex)">编辑</button>
                  <button class="btn btn--danger btn--sm" @click="remove(ex)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
