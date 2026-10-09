"""9 个输入特征与 6 类推荐输出的标准字典（T-2）。

统一字段名、取值范围与编码，供数据清洗（T-3）与特征编码（T-4）复用。
BMI 由身高、体重派生：bmi = weight_kg / (height_cm / 100) ** 2。
"""

# 9 个输入特征（用户画像）
FEATURES = {
    "gender": {
        "label": "性别",
        "type": "categorical",
        "values": ["男", "女"],
        "encode": {"男": 0, "女": 1},
    },
    "age": {"label": "年龄", "type": "numeric", "range": [14, 70]},
    "height_cm": {"label": "身高(cm)", "type": "numeric", "range": [140, 210]},
    "weight_kg": {"label": "体重(kg)", "type": "numeric", "range": [35, 200]},
    "goal": {
        "label": "运动目标",
        "type": "categorical",
        "values": ["减脂", "增肌", "塑形", "提升耐力", "保持健康"],
    },
    "experience_level": {
        "label": "运动基础",
        "type": "categorical",
        "values": ["新手", "初级", "中级", "高级"],
    },
    "weekly_hours": {"label": "每周可用时间(小时)", "type": "numeric", "range": [1, 21]},
    "diet_preference": {
        "label": "饮食偏好",
        "type": "categorical",
        "values": ["均衡", "高蛋白", "低碳水", "低脂", "素食"],
    },
    "injury": {
        "label": "运动伤病",
        "type": "multi_label",
        "values": ["无", "膝", "腰", "肩", "腕", "踝", "其他"],
    },
}

# 6 类推荐输出
OUTPUTS = {
    "target_goal": {
        "label": "训练目标",
        "type": "categorical",
        "values": ["减脂", "增肌", "塑形", "提升耐力", "保持健康"],
    },
    "weekly_frequency": {"label": "每周训练频率(次)", "type": "numeric", "range": [2, 6]},
    "exercise_plan": {"label": "动作组合", "type": "list"},
    "session_duration_min": {"label": "单次训练时长(分钟)", "type": "numeric", "range": [20, 90]},
    "intensity_level": {
        "label": "训练强度等级",
        "type": "categorical",
        "values": ["低", "中", "高"],
    },
    "training_cycle_weeks": {"label": "训练周期(周)", "type": "numeric", "range": [4, 12]},
}
