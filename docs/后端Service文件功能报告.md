# 后端Service文件功能报告

## 文档说明
本文档详细说明后端所有Service文件的功能、数据库关系和Redis使用情况，帮助快速了解代码结构。

**生成时间**: 2026-01-23  
**文件位置**: `backend/app/services/`

---

## 目录

1. [营养计算相关服务](#营养计算相关服务)
2. [推荐系统服务](#推荐系统服务)
3. [数据跟踪服务](#数据跟踪服务)
4. [社区功能服务](#社区功能服务)
5. [辅助功能服务](#辅助功能服务)

---

## 营养计算相关服务

### 1. calorie_calculator.py
**功能**: 基础代谢率(BMR)和总日能量消耗(TDEE)计算

#### 核心功能
- **BMR计算**: 
  - `calculate_bmr_mifflin_st_jeor()`: 使用Mifflin-St Jeor公式（需要性别、年龄、身高、体重）
  - `calculate_bmr_katch_mcardle()`: 使用Katch-McArdle公式（需要体脂率，更准确）
  - `calculate_bmr()`: 自动选择公式（优先Katch-McArdle）
- **TDEE计算**: `calculate_tdee()` - BMR × 活动水平系数
- **运动热量计算**: `calculate_exercise_calories_burned()` - 基于MET值

#### 数据库关系
- **读取**: `User` 模型
  - 字段: `weight_kg`, `height_cm`, `birthdate`, `gender`, `body_fat_pct`, `activity_level`
- **无写入操作**

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 无外部服务依赖
- 纯计算逻辑，无副作用

---

### 2. calorie_range_calculator.py
**功能**: 根据用户目标计算热量区间（最低/推荐/最高）

#### 核心功能
- `calculate_calorie_range()`: 主函数，根据目标返回热量区间
- 支持的目标:
  - **减脂** (`lose_weight`): 根据体脂率调整赤字幅度（10-30%）
  - **增肌** (`gain_muscle`): 根据训练经验调整盈余（5-20%）
  - **增重** (`gain_weight`): 10-20%盈余
  - **体态重组** (`body_recomposition`): 95-105% TDEE
  - **维持** (`maintain`): 95-105% TDEE

#### 数据库关系
- **读取**: `User` 模型
  - 字段: `goal`, `body_fat_pct`, `training_experience`
- **无写入操作**

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖: `calorie_calculator.py` (需要TDEE值)

---

### 3. macro_calculator.py
**功能**: 宏量营养素（蛋白质、脂肪、碳水化合物）计算

#### 核心功能
- `calculate_protein_requirement()`: 蛋白质需求（基于体重，g/kg）
  - 维持: 0.8-1.0 g/kg
  - 减脂/增肌: 1.6-2.2 g/kg
  - 体态重组: 2.0-2.4 g/kg
- `calculate_fat_requirement()`: 脂肪需求（基于总热量百分比）
  - 最低: 15-20%（保证必需脂肪酸）
  - 女性: 不低于25%（激素平衡）
- `calculate_carb_requirement()`: 碳水需求（剩余热量原则）
- `calculate_all_macros()`: 综合计算所有宏量营养素

#### 数据库关系
- **读取**: `User` 模型
  - 字段: `weight_kg`, `goal`, `gender`, `activity_level`, `training_experience`
- **无写入操作**

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 无外部依赖，纯计算逻辑

---

## 推荐系统服务

### 4. recommendation_service.py
**功能**: 营养推荐服务（整合所有计算和调整逻辑）

#### 核心功能
- `get_calorie_recommendation()`: 获取完整的营养推荐
  - 计算基础推荐（BMR/TDEE → 热量区间 → 宏量营养素）
  - Phase 2: 自动调整（基于历史数据）
  - Phase 4: 周期化营养调整（训练日/休息日）
  - Phase 4: 月经周期调整（仅女性）

#### 数据库关系
- **读取**: `User` 模型
  - 字段: 所有用户基础信息
- **间接写入**: 通过 `dynamic_adjustment_service` 写入 `recommendation_adjustments` 表

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖服务:
  - `calorie_calculator.py`
  - `calorie_range_calculator.py`
  - `macro_calculator.py`
  - `dynamic_adjustment_service.py`
  - `periodized_nutrition_service.py`
  - `menstrual_cycle_service.py`

---

### 5. dynamic_adjustment_service.py
**功能**: 基于历史数据的动态调整引擎

#### 核心功能
- `evaluate_and_adjust()`: 评估并自动调整推荐
  - 检查调整间隔（最小14天）
  - 多维度评估:
    - **体重变化**: 基于8周体重历史
    - **体脂率变化**: 基于8周体脂率历史
    - **执行情况**: 基于14天饮食日志
    - **训练表现**: 基于4周运动日志（Phase 3）
  - 综合决策并应用调整
  - 记录调整历史

#### 数据库关系
- **读取**:
  - `User` 模型
  - `body_metrics` 表（通过 `crud_body_metrics`）
  - `user_food_log` 表（通过 `crud_log`）
  - `user_exercise_log` 表（通过 `crud_log`）
  - `recommendation_adjustments` 表（通过 `crud_recommendation_history`）
- **写入**:
  - `recommendation_adjustments` 表（记录每次调整）

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖服务:
  - `calorie_calculator.py`
  - `calorie_range_calculator.py`
  - `macro_calculator.py`
  - `performance_analysis_service.py`
- 依赖CRUD:
  - `crud_body_metrics`
  - `crud_log`
  - `crud_recommendation_history`

---

### 6. periodized_nutrition_service.py
**功能**: 周期化营养策略（训练日/休息日差异化）

#### 核心功能
- `get_periodized_recommendation()`: 获取指定日期的周期化推荐
  - 判断是否为训练日（基于运动日志或活动水平）
  - 训练日: 增加热量和碳水
  - 休息日: 减少热量和碳水
- `get_weekly_periodized_plan()`: 生成一周的周期化计划

#### 数据库关系
- **读取**:
  - `User` 模型
  - `user_exercise_log` 表（通过 `crud_log`，用于判断训练日）
- **无写入操作**

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖服务:
  - `calorie_calculator.py`
  - `calorie_range_calculator.py`
  - `macro_calculator.py`
- 依赖CRUD:
  - `crud_log`

---

### 7. menstrual_cycle_service.py
**功能**: 女性月经周期营养调整

#### 核心功能
- `get_cycle_phase()`: 获取当前月经周期阶段
  - 四个阶段: 月经期、卵泡期、排卵期、黄体期
- `adjust_recommendation_for_cycle()`: 根据周期阶段调整推荐
  - 月经期: -50kcal, 碳水-2%
  - 卵泡期: 正常
  - 排卵期: +50kcal, 碳水+2%
  - 黄体期: +100kcal, 碳水+3%

#### 数据库关系
- **读取**: `User` 模型
  - 字段: `gender`, `last_period_start`
- **无写入操作**

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 无外部依赖，纯计算逻辑

---

### 8. performance_analysis_service.py
**功能**: 训练表现分析服务

#### 核心功能
- `analyze_training_performance()`: 分析用户训练表现
  - **总体趋势**: 训练量变化趋势
  - **力量训练趋势**: 基于关键词识别力量训练
  - **有氧训练趋势**: 基于关键词识别有氧训练
  - **训练频率**: 训练天数统计
  - **训练强度**: 基于平均MET值
  - **智能摘要**: 根据目标生成建议

#### 数据库关系
- **读取**:
  - `User` 模型
  - `user_exercise_log` 表（通过 `crud_log`）
  - `exercises` 表（关联查询，获取MET值）
- **无写入操作**

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖CRUD:
  - `crud_log`

---

## 数据跟踪服务

### 9. tracking_service.py
**功能**: 用户饮食和运动数据跟踪服务

#### 核心功能
- `get_daily_summary()`: 获取指定日期的每日总结
  - 计算总摄入（热量、蛋白质、脂肪、碳水）
  - 计算总消耗（BMR + 运动消耗）
  - 计算净热量
  - 获取推荐值对比
- `generate_ai_summary()`: 生成AI健康建议（使用智谱AI）
- `get_energy_summary()`: 获取能量摄入/消耗汇总（按日/月）

#### 数据库关系
- **读取**:
  - `User` 模型
  - `user_food_log` 表（通过 `crud_log`）
  - `user_exercise_log` 表（通过 `crud_log`）
  - `foods` 表（通过 `crud_food`，获取营养信息）
  - `exercises` 表（通过 `crud_exercise`，获取MET值）
- **无写入操作**

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖服务:
  - `calorie_calculator.py`
  - `recommendation_service.py`
- 依赖CRUD:
  - `crud_log`
  - `crud_food`
  - `crud_exercise`
- 外部API:
  - 智谱AI (ZhipuAI) - 用于生成AI建议

---

### 10. menu_generator.py
**功能**: AI菜单生成服务

#### 核心功能
- `generate_menu()`: 使用AI生成每日菜单
  - 从候选食物池中选择食物
  - 组合三餐（早餐、午餐、晚餐）
  - 满足热量和宏量营养素目标
- `verify_and_correct_menu()`: 验证并修正AI生成的菜单
  - 从数据库重新获取精确营养数据
  - 修正AI可能计算错误的数值
- `is_kcal_valid()`: 验证热量是否在允许范围内

#### 数据库关系
- **读取**:
  - `User` 模型
  - `foods` 表（通过 `crud_food`，获取候选食物和营养信息）
- **无写入操作**

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖CRUD:
  - `crud_food`
- 外部API:
  - 智谱AI (ZhipuAI) - 用于生成菜单

---

## 社区功能服务

### 11. blog_service.py
**功能**: 博客/动态服务

#### 核心功能
- `list_public()`: 获取公开博客列表
- `list_my()`: 获取当前用户的博客列表
- `create()`: 创建博客
- `get()`: 获取单个博客详情
- `update()`: 更新博客
- `delete()`: 删除博客
- `upload_images()`: 上传图片到腾讯云COS
- `_enrich_blogs_with_username()`: 丰富博客数据（添加用户名、图片、点赞状态等）

#### 数据库关系
- **读取**:
  - `blogs` 表（通过 `crud_blog`）
  - `users` 表（通过 `crud_user`，获取用户名）
  - `blog_images` 表（关联查询）
  - `blog_likes` 表（通过 `crud_blog_like`，检查点赞状态）
  - `blog_comments` 表（通过 `crud_blog_comment`，统计评论数）
- **写入**:
  - `blogs` 表
  - `blog_images` 表（图片上传时）

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖CRUD:
  - `crud_blog`
  - `crud_user`
  - `crud_blog_like`
  - `crud_blog_comment`
- 外部服务:
  - 腾讯云COS - 用于图片存储

---

### 12. notification_service.py
**功能**: 通知服务（处理点赞和评论通知）

#### 核心功能
- `notify_comment()`: 发送评论通知
  - 主评论: 通知帖子发布者
  - 回复主评论: 通知主评论发布者
  - 回复子评论: 通知被回复者和主评论发布者
- `notify_like()`: 发送点赞通知
  - 通知帖子发布者
- **频率限制**: 同一用户1分钟内对同一目标多次操作，只发送一次通知

#### 数据库关系
- **读取**:
  - `blogs` 表（通过 `crud_blog`）
  - `blog_comments` 表（通过 `crud_blog_comment`）
  - `notifications` 表（通过 `crud_notification`，检查频率限制）
- **写入**:
  - `notifications` 表（创建通知记录）

#### Redis关系
- **无Redis使用**

#### 依赖关系
- 依赖CRUD:
  - `crud_blog`
  - `crud_blog_comment`
  - `crud_notification`

---

### 13. ranking_service.py
**功能**: 排行榜服务（使用Redis Sorted Set实现实时排行榜）

#### 核心功能
- `update_ranking()`: 更新排行榜（用户记录运动时调用）
  - 更新总榜（日/月/年）
  - 更新身份分榜（日/月/年）
  - 使用Pipeline批量更新
  - 设置过期时间（日榜7天，月榜2个月，年榜1年）
- `get_top_rankings()`: 获取Top N排行榜
- `get_user_ranking()`: 获取用户排名和分数
- `update_user_identity()`: 用户身份变更时更新分榜

#### 数据库关系
- **读取**: `User` 模型（获取用户身份）
- **无直接数据库写入**（排行榜数据存储在Redis）

#### Redis关系
- **使用Redis Sorted Set (ZSET)**
- **Key格式**:
  - 总榜: `rank:global:{period}:{time_str}`
  - 分榜: `rank:category:{identity}:{period}:{time_str}`
- **Redis操作**:
  - `ZINCRBY`: 累加热量分数
  - `ZREVRANGE`: 获取Top N（降序）
  - `ZREVRANK`: 获取用户排名
  - `ZSCORE`: 获取用户分数
  - `ZREM`: 移除用户（身份变更时）
  - `ZADD`: 添加用户（身份变更时）
  - `EXPIRE`: 设置过期时间
  - `PIPELINE`: 批量操作

#### 依赖关系
- 依赖:
  - `app.db.redis_client.get_redis()` - 获取Redis客户端

---

## 服务依赖关系图

```
recommendation_service.py (核心推荐服务)
    ├── calorie_calculator.py
    ├── calorie_range_calculator.py
    ├── macro_calculator.py
    ├── dynamic_adjustment_service.py
    │   ├── performance_analysis_service.py
    │   └── (CRUD: body_metrics, log, recommendation_history)
    ├── periodized_nutrition_service.py
    │   └── (CRUD: log)
    └── menstrual_cycle_service.py

tracking_service.py
    ├── calorie_calculator.py
    ├── recommendation_service.py
    └── (CRUD: log, food, exercise)

menu_generator.py
    └── (CRUD: food)
    └── (外部API: 智谱AI)

ranking_service.py
    └── (Redis: Sorted Set)

blog_service.py
    └── (CRUD: blog, user, blog_like, blog_comment)
    └── (外部服务: 腾讯云COS)

notification_service.py
    └── (CRUD: blog, blog_comment, notification)
```

---

## 数据库表关系总结

### 主要读取的表
- **users**: 用户基础信息（所有服务）
- **user_food_log**: 饮食记录（tracking_service, dynamic_adjustment_service）
- **user_exercise_log**: 运动记录（tracking_service, dynamic_adjustment_service, performance_analysis_service, periodized_nutrition_service）
- **body_metrics**: 身体指标记录（dynamic_adjustment_service）
- **recommendation_adjustments**: 推荐调整历史（dynamic_adjustment_service）
- **foods**: 食物信息（tracking_service, menu_generator）
- **exercises**: 运动信息（tracking_service, performance_analysis_service）
- **blogs**: 博客/动态（blog_service, notification_service）
- **blog_images**: 博客图片（blog_service）
- **blog_likes**: 点赞记录（blog_service）
- **blog_comments**: 评论记录（blog_service, notification_service）
- **notifications**: 通知记录（notification_service）

### 主要写入的表
- **recommendation_adjustments**: 推荐调整历史（dynamic_adjustment_service）
- **blogs**: 博客创建/更新（blog_service）
- **blog_images**: 图片上传（blog_service）
- **notifications**: 通知创建（notification_service）

---

## Redis使用总结

### 使用Redis的服务
- **ranking_service.py**: 唯一使用Redis的服务

### Redis数据结构
- **Sorted Set (ZSET)**: 用于排行榜
  - Member: 用户ID（字符串）
  - Score: 消耗的热量（浮点数）

### Redis Key命名规范
- 总榜: `rank:global:{period}:{time_str}`
  - 示例: `rank:global:day:20260123`
- 分榜: `rank:category:{identity}:{period}:{time_str}`
  - 示例: `rank:category:student:day:20260123`

### Redis过期策略
- 日榜: 7天
- 月榜: 60天
- 年榜: 365天

---

## 外部服务依赖

### AI服务
- **智谱AI (ZhipuAI)**
  - 使用服务: `tracking_service.py`, `menu_generator.py`
  - 用途: 生成AI健康建议、生成菜单

### 云存储服务
- **腾讯云COS**
  - 使用服务: `blog_service.py`
  - 用途: 存储博客图片

---

## 服务分类统计

### 纯计算服务（无数据库/Redis）
- `calorie_calculator.py`
- `calorie_range_calculator.py`
- `macro_calculator.py`
- `menstrual_cycle_service.py`

### 数据库读取服务
- `recommendation_service.py`（整合服务）
- `dynamic_adjustment_service.py`（读取+写入）
- `periodized_nutrition_service.py`
- `performance_analysis_service.py`
- `tracking_service.py`
- `menu_generator.py`
- `blog_service.py`（读取+写入）
- `notification_service.py`（读取+写入）

### Redis服务
- `ranking_service.py`（唯一使用Redis的服务）

---

## 关键设计模式

1. **服务分层**: 计算服务 → 推荐服务 → 调整服务
2. **依赖注入**: 通过参数传递数据库会话
3. **单一职责**: 每个服务专注于特定功能
4. **组合模式**: `recommendation_service` 组合多个子服务
5. **策略模式**: 不同目标使用不同的计算策略

---

## 性能考虑

### 数据库查询优化
- 使用 `joinedload` 预加载关联数据（tracking_service）
- 使用索引查询（所有CRUD操作）
- 批量操作使用Pipeline（ranking_service Redis操作）

### 缓存策略
- Redis用于排行榜（高频读取，实时更新）
- 无其他缓存（可考虑添加推荐结果缓存）

### 外部API调用
- AI服务调用有重试机制（menu_generator）
- 图片上传使用异步处理（blog_service）

---

**文档版本**: v1.0  
**最后更新**: 2026-01-23
