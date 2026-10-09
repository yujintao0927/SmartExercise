<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const GOALS = ['减脂', '增肌', '塑形', '提升耐力', '保持健康']
const EXPERIENCES = ['新手', '初级', '中级', '高级']
const DIETS = ['均衡', '高蛋白', '低碳水', '低脂', '素食']
const INJURIES = ['无', '膝', '腰', '肩', '腕', '踝', '其他']

const form = ref({
  gender: 0,
  age: 25,
  height_cm: 175,
  weight_kg: 70,
  goal: '增肌',
  experience_level: '初级',
  weekly_hours: 6,
  diet_preference: '高蛋白',
  injury: ['无'],
})

const error = ref('')
const saving = ref(false)

function toggleInjury(part) {
  if (part === '无') {
    form.value.injury = ['无']
    return
  }
  const list = form.value.injury.filter((p) => p !== '无')
  const i = list.indexOf(part)
  if (i >= 0) list.splice(i, 1)
  else list.push(part)
  form.value.injury = list.length ? list : ['无']
}

async function submit() {
  error.value = ''
  saving.value = true
  try {
    await api.put('/profile', form.value)
    router.push('/recommend')
  } catch (e) {
    const d = e.response?.data?.detail
    error.value = Array.isArray(d) ? d[0]?.msg || '输入不合法' : d || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="fade-up">
    <span class="tag">Profile</span>
    <h1 class="title">录入<span class="accent">画像</span></h1>
    <p class="muted">9 项身体与习惯特征，用于生成个性化计划</p>

    <form class="card form" @submit.prevent="submit">
      <div class="grid">
        <div class="field">
          <label>性别</label>
          <select v-model.number="form.gender">
            <option :value="0">男</option>
            <option :value="1">女</option>
          </select>
        </div>
        <div class="field">
          <label>年龄</label>
          <input v-model.number="form.age" type="number" min="14" max="70" required />
        </div>
        <div class="field">
          <label>身高 (cm)</label>
          <input v-model.number="form.height_cm" type="number" min="140" max="210" step="0.1" required />
        </div>
        <div class="field">
          <label>体重 (kg)</label>
          <input v-model.number="form.weight_kg" type="number" min="35" max="200" step="0.1" required />
        </div>
        <div class="field">
          <label>运动目标</label>
          <select v-model="form.goal">
            <option v-for="g in GOALS" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>
        <div class="field">
          <label>运动基础</label>
          <select v-model="form.experience_level">
            <option v-for="e in EXPERIENCES" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>
        <div class="field">
          <label>每周可用时间 (小时)</label>
          <input v-model.number="form.weekly_hours" type="number" min="1" max="21" step="0.5" required />
        </div>
        <div class="field">
          <label>饮食偏好</label>
          <select v-model="form.diet_preference">
            <option v-for="d in DIETS" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label>运动伤病（可多选，「无」与其他互斥）</label>
        <div class="chips">
          <button
            v-for="p in INJURIES"
            :key="p"
            type="button"
            class="chip"
            :class="{ 'chip--on': form.injury.includes(p) }"
            @click="toggleInjury(p)"
          >
            {{ p }}
          </button>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
      <button class="btn" type="submit" :disabled="saving">
        {{ saving ? '保存中…' : '保存并生成推荐' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.title {
  font-size: clamp(2rem, 5vw, 3.4rem);
  margin: 8px 0 4px;
}

.accent {
  color: var(--accent);
}

.form {
  margin-top: 28px;
  padding: 28px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0 20px;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  background: var(--bg-elevated);
  border: 1px solid var(--line);
  border-radius: 2px;
  color: var(--text-muted);
  padding: 8px 16px;
  font-weight: 600;
  transition: all 0.15s ease;
}

.chip--on {
  border-color: var(--accent);
  color: var(--accent);
  background: rgba(200, 255, 0, 0.06);
}

.error {
  color: var(--danger);
  margin-bottom: 14px;
}
</style>
