"""规则引擎：9 个输入特征 → 6 类推荐输出（T-4）。

基于健身常识与 MealPlan 规则，把用户画像映射为结构化训练计划。
用于生成训练集（随机森林学习该映射）与在线推理的动作组合组装。
"""
from .feature_dictionary import FEATURES

# 动作库：按「目标 × 强度」映射到动作名称列表（T-8a 迁移到数据库字典表）
EXERCISES = {
    ("减脂", "低"): ["快走", "椭圆机", "瑜伽", "平板支撑"],
    ("减脂", "中"): ["慢跑", "动感单车", "深蹲", "波比跳"],
    ("减脂", "高"): ["HIIT", "跳绳", "划船机", "登山跑"],
    ("增肌", "低"): ["器械推胸", "腿举", "坐姿划船", "卷腹"],
    ("增肌", "中"): ["卧推", "深蹲", "硬拉", "引体向上"],
    ("增肌", "高"): ["大重量卧推", "大重量深蹲", "硬拉", "肩推"],
    ("塑形", "低"): ["普拉提", "弹力带训练", "臀桥", "侧平板"],
    ("塑形", "中"): ["深蹲", "箭步蹲", "俯卧撑", "山羊挺身"],
    ("塑形", "高"): ["负重深蹲", "罗马尼亚硬拉", "绳索夹胸", "臀推"],
    ("提升耐力", "低"): ["快走", "骑行", "游泳", "划船"],
    ("提升耐力", "中"): ["慢跑", "动感单车", "游泳", "跳绳"],
    ("提升耐力", "高"): ["长跑", "间歇跑", "骑行爬坡", "划船机"],
    ("保持健康", "低"): ["散步", "太极", "拉伸", "瑜伽"],
    ("保持健康", "中"): ["快走", "骑行", "游泳", "徒手深蹲"],
    ("保持健康", "高"): ["慢跑", "游泳", "划船", "全身循环"],
}

_CYCLE = {"减脂": 8, "增肌": 10, "塑形": 6, "提升耐力": 8, "保持健康": 6}


def recommend(gender, age, height_cm, weight_kg, goal, experience_level,
              weekly_hours, diet_preference, injury):
    """由 9 特征计算 6 类推荐结果。"""
    target_goal = goal

    # 强度等级：基础水平 - 伤病/高龄降档，高级增肌封顶高档
    level = {"新手": 0, "初级": 1, "中级": 2, "高级": 3}.get(experience_level, 1)
    if injury and injury != "无":
        level -= 1
    if age > 50:
        level -= 1
    if goal == "增肌" and experience_level == "高级":
        level = 3
    level = max(0, min(level, 2))
    intensity = ["低", "中", "高"][level]

    # 每周训练频率：随可用时间递增
    if weekly_hours < 3:
        freq = 2
    elif weekly_hours < 6:
        freq = 3
    elif weekly_hours < 10:
        freq = 4
    elif weekly_hours < 15:
        freq = 5
    else:
        freq = 6

    # 单次训练时长
    duration = 40 + level * 10 + (20 if goal == "增肌" else 0)
    duration = max(20, min(90, duration))

    # 训练周期
    cycle = _CYCLE.get(goal, 6)

    # 动作组合
    exercises = EXERCISES.get((goal, intensity), EXERCISES[("保持健康", "低")])

    return {
        "target_goal": target_goal,
        "weekly_frequency": freq,
        "exercise_plan": exercises,
        "session_duration_min": duration,
        "intensity_level": intensity,
        "training_cycle_weeks": cycle,
    }
