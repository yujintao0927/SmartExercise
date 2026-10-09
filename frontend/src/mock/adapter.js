// mock axios adapter：拦截请求并返回假数据，后续切换真实接口时只需关闭 USE_MOCK。
import { db, genPassword } from './db'

const delay = (ms) => new Promise((r) => setTimeout(r, ms))

// 当前登录用户的画像（mock 会话态）
let profile = {
  gender: 0, age: 25, height_cm: 175, weight_kg: 70,
  goal: '增肌', experience_level: '初级', weekly_hours: 6,
  diet_preference: '高蛋白', injury: ['无'],
}

function resp(data, status = 200) {
  return { data, status, statusText: status >= 400 ? 'Error' : 'OK', headers: {}, config: {} }
}

function makePlan() {
  return db.exercises.slice(0, 4).map((e) => ({ name: e.name, sets: 4, reps: 8 }))
}

function findUser(id) {
  return db.users.find((u) => u.id === Number(id))
}

function calcStats() {
  const t = db.training
  const now = Date.now()
  const week = t.filter((r) => now - new Date(r.train_date).getTime() < 7 * 86400000)
  const weekAvg = week.length
    ? week.reduce((s, r) => s + r.completion_rate, 0) / week.length
    : 0
  return {
    streak_days: 5,
    total_sessions: t.length,
    week_sessions: week.length,
    week_completion_avg: Math.round(weekAvg * 100) / 100,
  }
}

export default async function mockAdapter(config) {
  await delay(140)
  const method = (config.method || 'get').toLowerCase()
  const url = ((config.url || '').split('/api')[1]) || config.url
  let body = {}
  if (config.data) {
    try { body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data } catch { body = {} }
  }
  const params = config.params || {}

  // ---------- 认证 ----------
  if (method === 'post' && url === '/auth/register') {
    if (db.users.some((u) => u.username === body.username)) return resp({ detail: '用户名已存在' }, 409)
    const user = { id: db.users.length + 1, username: body.username, role: 'user', active: true, created_at: new Date().toISOString() }
    db.users.push(user)
    db.currentUser = user
    return resp({ id: user.id, username: user.username }, 201)
  }

  if (method === 'post' && url === '/auth/login') {
    const user = db.users.find((u) => u.username === body.username)
    if (!user) return resp({ detail: '用户名或密码错误' }, 401)
    db.currentUser = user
    return resp({ access_token: `mock-token-${user.role}`, token_type: 'bearer' })
  }

  if (method === 'get' && url === '/auth/me') {
    if (!db.currentUser) return resp({ detail: '未认证' }, 401)
    const { id, username, role, created_at } = db.currentUser
    return resp({ id, username, role, created_at })
  }

  if (method === 'put' && url === '/auth/password') {
    return resp({ message: '密码已更新' })
  }

  // ---------- 画像 ----------
  if (method === 'put' && url === '/profile') {
    profile = { ...profile, ...body }
    return resp(profile)
  }
  if (method === 'get' && url === '/profile') {
    return resp(profile)
  }

  // ---------- 推荐 ----------
  if (method === 'post' && url === '/recommend') {
    const rec = {
      id: db.recommendations.length + 1,
      target_goal: '增肌', weekly_frequency: 4, session_duration_min: 60,
      intensity_level: '中', training_cycle_weeks: 8, model_version: 'rf-v1.0',
      exercise_plan: makePlan(),
      created_at: new Date().toISOString(),
    }
    db.recommendations.unshift(rec)
    return resp({
      target_goal: rec.target_goal, weekly_frequency: rec.weekly_frequency,
      exercise_plan: rec.exercise_plan, session_duration_min: rec.session_duration_min,
      intensity_level: rec.intensity_level, training_cycle_weeks: rec.training_cycle_weeks,
      model_version: rec.model_version,
    })
  }
  if (method === 'get' && url === '/recommend/history') {
    return resp(db.recommendations)
  }

  // ---------- 训练 ----------
  if (method === 'post' && url === '/training/records') {
    const rec = { id: db.training.length + 1, ...body }
    db.training.unshift(rec)
    return resp({ id: rec.id }, 201)
  }
  if (method === 'get' && url === '/training/records') {
    return resp([...db.training].sort((a, b) => (a.train_date < b.train_date ? 1 : -1)))
  }
  if (method === 'get' && url === '/training/stats') {
    return resp(calcStats())
  }

  // ---------- 身体 / 仪表盘 ----------
  if (method === 'post' && url === '/metrics/weight') {
    const bmi = profile.height_cm ? Math.round((body.weight_kg / (profile.height_cm / 100) ** 2) * 10) / 10 : null
    const rec = { id: db.weight.length + 1, record_date: body.record_date, weight_kg: body.weight_kg, bmi }
    db.weight.unshift(rec)
    return resp({ id: rec.id, bmi }, 201)
  }
  if (method === 'get' && url === '/metrics/weight') {
    return resp([...db.weight].sort((a, b) => (a.record_date < b.record_date ? 1 : -1)))
  }
  if (method === 'get' && url === '/dashboard/summary') {
    return resp({
      training: [...db.training].sort((a, b) => (a.train_date > b.train_date ? 1 : -1))
        .map((r) => ({ date: r.train_date, completion_rate: r.completion_rate, fatigue_score: r.fatigue_score })),
      weight: [...db.weight].sort((a, b) => (a.record_date > b.record_date ? 1 : -1))
        .map((w) => ({ date: w.record_date, weight_kg: w.weight_kg })),
      adjustment: { available: true, frequency_delta: 0, intensity_delta: 0, advice: '完成率与疲劳适中，维持当前训练计划' },
    })
  }

  // ---------- 管理员：总览 / 模型 ----------
  if (method === 'get' && url === '/admin/overview') {
    return resp(db.overview)
  }
  if (method === 'get' && url === '/admin/model') {
    return resp({
      loaded: true,
      best_params: { max_depth: 10, n_estimators: 50 },
      metrics: {
        target_goal: { accuracy: 1.0, f1: 1.0 },
        weekly_frequency: { accuracy: 0.9874, f1: 0.9872 },
        session_duration_min: { accuracy: 0.9999, f1: 0.9999 },
        intensity_level: { accuracy: 0.9989, f1: 0.9989 },
        training_cycle_weeks: { accuracy: 0.9729, f1: 0.9725 },
      },
    })
  }

  // ---------- 管理员：用户 ----------
  if (method === 'get' && url === '/admin/users') {
    let list = [...db.users]
    if (params.search) list = list.filter((u) => u.username.includes(params.search))
    if (params.role) list = list.filter((u) => u.role === params.role)
    return resp({ items: list, total: list.length, page: 1, page_size: 100 })
  }

  let m = url.match(/^\/admin\/users\/(\d+)$/)
  if (m) {
    const user = findUser(m[1])
    if (!user) return resp({ detail: '用户不存在' }, 404)
    if (method === 'get') {
      return resp({
        ...user,
        profile: { age: 25, goal: '增肌', height_cm: 175, weight_kg: 70 },
        recent_training: db.training.slice(0, 3).map((r) => ({ train_date: r.train_date, completion_rate: r.completion_rate })),
        recent_recommendations: db.recommendations.slice(0, 2).map((r) => ({ target_goal: r.target_goal, created_at: r.created_at })),
      })
    }
    if (method === 'patch') {
      user.active = body.active
      return resp({ id: user.id, active: user.active })
    }
    if (method === 'delete') {
      db.users = db.users.filter((u) => u.id !== user.id)
      return resp({ message: '已删除' })
    }
    if (method === 'post') {
      const pwd = body.new_password || genPassword()
      return resp({ username: user.username, new_password: pwd })
    }
  }

  // ---------- 管理员：推荐 / 训练 ----------
  if (method === 'get' && url === '/admin/recommendations') {
    const items = db.recommendations.map((r) => ({
      id: r.id, user_id: 1, username: 'demo', target_goal: r.target_goal,
      intensity_level: r.intensity_level, created_at: r.created_at,
    }))
    return resp({ items, total: items.length })
  }
  if (method === 'get' && url === '/admin/training') {
    return resp({
      total_sessions: 1024,
      avg_completion: 0.78,
      avg_fatigue: 5.2,
      completion_distribution: db.overview.completion_distribution,
    })
  }

  // ---------- 管理员：动作库 ----------
  if (method === 'get' && url === '/admin/exercises') {
    let list = [...db.exercises]
    if (params.muscle_group) list = list.filter((e) => e.muscle_group === params.muscle_group)
    if (params.exercise_type) list = list.filter((e) => e.exercise_type === params.exercise_type)
    return resp(list)
  }
  if (method === 'post' && url === '/admin/exercises') {
    const ex = { id: db.exercises.length + 1, ...body }
    db.exercises.push(ex)
    return resp(ex, 201)
  }
  let em = url.match(/^\/admin\/exercises\/(\d+)$/)
  if (em) {
    const ex = db.exercises.find((e) => e.id === Number(em[1]))
    if (!ex) return resp({ detail: '动作不存在' }, 404)
    if (method === 'put') { Object.assign(ex, body); return resp(ex) }
    if (method === 'delete') { db.exercises = db.exercises.filter((e) => e.id !== ex.id); return resp({ message: '已删除' }) }
  }

  // ---------- 管理员：模板 ----------
  if (method === 'get' && url === '/admin/templates') {
    let list = [...db.templates]
    if (params.goal) list = list.filter((t) => t.goal === params.goal)
    if (params.intensity_level) list = list.filter((t) => t.intensity_level === params.intensity_level)
    return resp(list)
  }
  if (method === 'post' && url === '/admin/templates') {
    const tpl = { id: db.templates.length + 1, ...body }
    db.templates.push(tpl)
    return resp(tpl, 201)
  }
  let tm = url.match(/^\/admin\/templates\/(\d+)$/)
  if (tm) {
    const tpl = db.templates.find((t) => t.id === Number(tm[1]))
    if (!tpl) return resp({ detail: '模板不存在' }, 404)
    if (method === 'put') { Object.assign(tpl, body); return resp(tpl) }
    if (method === 'delete') { db.templates = db.templates.filter((t) => t.id !== tpl.id); return resp({ message: '已删除' }) }
  }

  return resp({ detail: `mock 未实现: ${method.toUpperCase()} ${url}` }, 404)
}
