// mock 数据层：前端在接口实现前使用的假数据。
// 所有数据为模块级可变状态，页面刷新后重置，用于 UI 联调与演示。

const d = (n) => `2026-10-${String(n).padStart(2, '0')}`

export const db = {
  currentUser: null,

  // 用户列表（管理员可见）
  users: [
    { id: 1, username: 'demo', role: 'user', active: true, created_at: '2026-09-01T09:12:00' },
    { id: 2, username: 'lin_strong', role: 'user', active: true, created_at: '2026-09-03T14:30:00' },
    { id: 3, username: 'momo', role: 'user', active: true, created_at: '2026-09-06T10:02:00' },
    { id: 4, username: 'fit_chen', role: 'user', active: true, created_at: '2026-09-10T18:44:00' },
    { id: 5, username: 'iron_li', role: 'user', active: false, created_at: '2026-09-12T08:15:00' },
    { id: 6, username: 'runner_zhao', role: 'user', active: true, created_at: '2026-09-15T20:20:00' },
    { id: 7, username: 'yoga_wang', role: 'user', active: true, created_at: '2026-09-20T12:08:00' },
    { id: 8, username: 'power_sun', role: 'user', active: true, created_at: '2026-09-25T16:50:00' },
    { id: 100, username: 'admin', role: 'admin', active: true, created_at: '2026-08-20T09:00:00' },
  ],

  // 当前用户（demo）训练记录
  training: [
    { id: 15, train_date: '2026-10-08', completion_rate: 0.9, fatigue_score: 4, feedback: '适中', duration_min: 62 },
    { id: 14, train_date: '2026-10-06', completion_rate: 0.8, fatigue_score: 5, feedback: '适中', duration_min: 58 },
    { id: 13, train_date: '2026-10-04', completion_rate: 1.0, fatigue_score: 3, feedback: '太轻松', duration_min: 60 },
    { id: 12, train_date: '2026-10-02', completion_rate: 0.7, fatigue_score: 6, feedback: '适中', duration_min: 55 },
    { id: 11, train_date: '2026-09-30', completion_rate: 0.9, fatigue_score: 4, feedback: '适中', duration_min: 61 },
    { id: 10, train_date: '2026-09-28', completion_rate: 0.6, fatigue_score: 7, feedback: '太累', duration_min: 50 },
    { id: 9, train_date: '2026-09-25', completion_rate: 0.9, fatigue_score: 4, feedback: '适中', duration_min: 63 },
    { id: 8, train_date: '2026-09-22', completion_rate: 0.8, fatigue_score: 5, feedback: '适中', duration_min: 59 },
    { id: 7, train_date: '2026-09-19', completion_rate: 1.0, fatigue_score: 3, feedback: '太轻松', duration_min: 60 },
    { id: 6, train_date: '2026-09-16', completion_rate: 0.7, fatigue_score: 6, feedback: '适中', duration_min: 54 },
    { id: 5, train_date: '2026-09-13', completion_rate: 0.9, fatigue_score: 4, feedback: '适中', duration_min: 62 },
    { id: 4, train_date: '2026-09-10', completion_rate: 0.8, fatigue_score: 5, feedback: '适中', duration_min: 57 },
    { id: 3, train_date: '2026-09-07', completion_rate: 0.5, fatigue_score: 8, feedback: '太累', duration_min: 45 },
    { id: 2, train_date: '2026-09-04', completion_rate: 0.9, fatigue_score: 4, feedback: '适中', duration_min: 60 },
    { id: 1, train_date: '2026-09-01', completion_rate: 0.7, fatigue_score: 6, feedback: '适中', duration_min: 52 },
  ],

  // 当前用户体重记录
  weight: [
    { id: 10, record_date: '2026-10-08', weight_kg: 68.2, bmi: 22.3 },
    { id: 9, record_date: '2026-10-01', weight_kg: 68.6, bmi: 22.4 },
    { id: 8, record_date: '2026-09-24', weight_kg: 69.0, bmi: 22.5 },
    { id: 7, record_date: '2026-09-17', weight_kg: 69.3, bmi: 22.6 },
    { id: 6, record_date: '2026-09-10', weight_kg: 69.7, bmi: 22.8 },
    { id: 5, record_date: '2026-09-03', weight_kg: 70.1, bmi: 22.9 },
    { id: 4, record_date: '2026-08-27', weight_kg: 70.5, bmi: 23.0 },
    { id: 3, record_date: '2026-08-20', weight_kg: 70.9, bmi: 23.1 },
    { id: 2, record_date: '2026-08-13', weight_kg: 71.3, bmi: 23.3 },
    { id: 1, record_date: '2026-08-06', weight_kg: 71.8, bmi: 23.4 },
  ],

  // 当前用户推荐历史
  recommendations: [
    { id: 3, target_goal: '增肌', weekly_frequency: 4, session_duration_min: 60, intensity_level: '中', training_cycle_weeks: 8, model_version: 'rf-v1.0', created_at: '2026-10-08T10:00:00' },
    { id: 2, target_goal: '增肌', weekly_frequency: 3, session_duration_min: 50, intensity_level: '低', training_cycle_weeks: 6, model_version: 'rf-v1.0', created_at: '2026-09-15T10:00:00' },
    { id: 1, target_goal: '减脂', weekly_frequency: 5, session_duration_min: 45, intensity_level: '中', training_cycle_weeks: 8, model_version: 'rf-v0.9', created_at: '2026-09-01T10:00:00' },
  ],

  // 动作库
  exercises: [
    { id: 1, name: '硬拉', muscle_group: '背', exercise_type: '力量' },
    { id: 2, name: '深蹲', muscle_group: '腿', exercise_type: '力量' },
    { id: 3, name: '卧推', muscle_group: '胸', exercise_type: '力量' },
    { id: 4, name: '引体向上', muscle_group: '背', exercise_type: '力量' },
    { id: 5, name: '肩推', muscle_group: '肩', exercise_type: '力量' },
    { id: 6, name: '划船', muscle_group: '背', exercise_type: '力量' },
    { id: 7, name: '箭步蹲', muscle_group: '腿', exercise_type: '力量' },
    { id: 8, name: '俯卧撑', muscle_group: '胸', exercise_type: '力量' },
    { id: 9, name: '平板支撑', muscle_group: '核心', exercise_type: '力量' },
    { id: 10, name: '跑步', muscle_group: '全身', exercise_type: '有氧' },
    { id: 11, name: '骑行', muscle_group: '全身', exercise_type: '有氧' },
    { id: 12, name: '拉伸', muscle_group: '全身', exercise_type: '柔韧' },
  ],

  // 计划模板
  templates: [
    { id: 1, goal: '增肌', intensity_level: '中', exercise_ids: [1, 2, 3, 4], sets: 4, reps: 8, session_duration_min: 60, weekly_frequency: 4, training_cycle_weeks: 8 },
    { id: 2, goal: '增肌', intensity_level: '高', exercise_ids: [1, 2, 3, 5], sets: 5, reps: 6, session_duration_min: 70, weekly_frequency: 5, training_cycle_weeks: 10 },
    { id: 3, goal: '减脂', intensity_level: '中', exercise_ids: [10, 11, 8, 9], sets: 4, reps: 15, session_duration_min: 45, weekly_frequency: 5, training_cycle_weeks: 8 },
    { id: 4, goal: '减脂', intensity_level: '低', exercise_ids: [10, 12, 8, 9], sets: 3, reps: 12, session_duration_min: 40, weekly_frequency: 3, training_cycle_weeks: 6 },
    { id: 5, goal: '塑形', intensity_level: '中', exercise_ids: [8, 5, 7, 9], sets: 4, reps: 12, session_duration_min: 50, weekly_frequency: 4, training_cycle_weeks: 8 },
    { id: 6, goal: '提升耐力', intensity_level: '中', exercise_ids: [10, 11, 8, 9], sets: 3, reps: 15, session_duration_min: 55, weekly_frequency: 4, training_cycle_weeks: 6 },
  ],

  // 管理员数据总览
  overview: {
    kpi: { total_users: 128, new_users_today: 3, total_recommendations: 512, total_sessions: 1024, active_users_week: 45 },
    user_growth: [
      { date: '09-20', count: 4 }, { date: '09-22', count: 6 }, { date: '09-24', count: 5 },
      { date: '09-26', count: 9 }, { date: '09-28', count: 7 }, { date: '09-30', count: 11 },
      { date: '10-02', count: 8 }, { date: '10-04', count: 13 }, { date: '10-06', count: 10 }, { date: '10-08', count: 12 },
    ],
    goal_distribution: [
      { goal: '增肌', count: 42 }, { goal: '减脂', count: 38 }, { goal: '塑形', count: 22 },
      { goal: '保持健康', count: 16 }, { goal: '提升耐力', count: 10 },
    ],
    completion_distribution: [
      { range: '80-100%', count: 62 }, { range: '60-80%', count: 34 },
      { range: '40-60%', count: 12 }, { range: '0-40%', count: 6 },
    ],
  },
}

// 生成新密码（mock 重置密码用）
export function genPassword() {
  return 'fl' + Math.random().toString(36).slice(2, 8)
}
