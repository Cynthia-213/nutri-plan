-- 数据库初始化脚本 for Nutri-Plan

CREATE DATABASE IF NOT EXISTS nutri_plan CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nutri_plan;

--
-- 用户表 (users)
-- 存储用户的基本信息、身体数据和健康目标
--
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL UNIQUE COMMENT '用户名',
    `email` VARCHAR(255) NOT NULL UNIQUE COMMENT '电子邮箱',
    `hashed_password` VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    `gender` ENUM('male', 'female', 'unwilling_to_disclose') COMMENT '性别',
    `birthdate` DATE COMMENT '出生日期',
    `height_cm` DECIMAL(5, 2) COMMENT '身高（厘米）',
    `weight_kg` DECIMAL(5, 2) COMMENT '体重（公斤）',
    `activity_level` ENUM('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active') DEFAULT 'sedentary' COMMENT '日常活动水平',
    `goal` ENUM('maintain', 'lose_weight', 'gain_muscle') DEFAULT 'maintain' COMMENT '健康目标',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='用户信息表';


DROP TABLE IF EXISTS `foods`;

CREATE TABLE IF NOT EXISTS `foods` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `description_zh` VARCHAR(255) COMMENT '中文食物名称或描述',
    `description_en` VARCHAR(255) COMMENT '英文食物名称或描述',
    `energy_kcal` DECIMAL(10, 2) COMMENT '每100克所含热量（千卡）',
    `protein_g` DECIMAL(10, 2) COMMENT '每100克所含蛋白质（克）',
    `fat_g` DECIMAL(10, 2) COMMENT '每100克所含脂肪（克）',
    `carbohydrate_g` DECIMAL(10, 2) COMMENT '每100克所含碳水化合物（克）',
    `fiber_total_dietary_g` DECIMAL(10, 2) COMMENT '每100克所含膳食纤维（克）',
    `sugars_g` DECIMAL(10, 2) COMMENT '每100克所含糖（克）',
    `fe_mg` DECIMAL(10, 2) COMMENT '每100克所含铁（毫克）',
    `na_mg` DECIMAL(10, 2) COMMENT '每100克所含钠（毫克）',
    `serving_size_g` DECIMAL(10, 2) DEFAULT 100.00 COMMENT '常见份量（克）',
    `source` VARCHAR(100) COMMENT '数据来源',
    `is_high_protein` BOOLEAN DEFAULT FALSE COMMENT '是否高蛋白（蛋白供能比>20%）' AFTER `protein_g`,
    `is_low_carb` BOOLEAN DEFAULT FALSE COMMENT '是否低碳水（每100g碳水<10g）' AFTER `carbohydrate_g`,
    `is_low_fat` BOOLEAN DEFAULT FALSE COMMENT '是否低脂（脂肪供能比<15%）' AFTER `fat_g`,
    `is_high_fiber` BOOLEAN DEFAULT FALSE COMMENT '是否高纤维（每100g膳食纤维>3g）' AFTER `fiber_total_dietary_g`,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='食物营养信息表';

UPDATE `foods` 
SET 
  `is_high_protein` = IF(`energy_kcal` > 0 AND (`protein_g` * 4.0 / `energy_kcal`) > 0.2, TRUE, FALSE),
  `is_low_carb` = IF(`carbohydrate_g` < 10, TRUE, FALSE),
  `is_low_fat` = IF(`energy_kcal` > 0 AND (`fat_g` * 9.0 / `energy_kcal`) < 0.15, TRUE, FALSE),
  `is_high_fiber` = IF(`fiber_total_dietary_g` > 3, TRUE, FALSE);

--
-- 运动表 (exercises)
-- 存储运动项目及其代谢当量（MET, Metabolic Equivalent of Task）
-- MET值是计算运动消耗热量的关键系数
--
CREATE TABLE IF NOT EXISTS `exercises` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE COMMENT '运动名称',
    `met_value` DECIMAL(4, 2) NOT NULL COMMENT '代谢当量(MET)',
    `description` TEXT COMMENT '运动描述',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT='运动热量消耗系数表';

--
-- 用户饮食记录表 (user_food_log)
-- 记录用户每日摄入的食物
--
CREATE TABLE IF NOT EXISTS `user_food_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '逻辑外键, 关联 users.id',
    `food_id` INT NOT NULL COMMENT '逻辑外键, 关联 foods.id',
    `serving_grams` DECIMAL(10, 2) NOT NULL COMMENT '摄入份量（克）',
    `log_date` DATE NOT NULL COMMENT '记录日期',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT='用户每日饮食记录表';

--
-- 用户运动记录表 (user_exercise_log)
-- 记录用户每日的运动活动
--
DROP TABLE IF EXISTS `user_exercise_log`;
CREATE TABLE IF NOT EXISTS `user_exercise_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '逻辑外键, 关联 users.id',
    `exercise_id` INT NOT NULL COMMENT '逻辑外键, 关联 exercises.id',
    `duration_minutes` INT NOT NULL COMMENT '运动时长（分钟）',
    `calories_burned` DECIMAL(10, 2) NOT NULL COMMENT '消耗热量（千卡）',
    `log_date` DATE NOT NULL COMMENT '记录日期',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT='用户每日运动记录表';

--
-- 插入一些常见的运动及其MET值作为初始数据
--
INSERT INTO `exercises` (`name`, `met_value`, `description`) VALUES
('静坐', 1.0, '安静地坐着，例如看电视、阅读。'),
('散步 (慢速)', 2.0, '在平地上以悠闲的速度行走。'),
('散步 (中速)', 3.5, '以普通速度行走，例如通勤步行。'),
('快走', 4.3, '以较快的速度行走，心率轻微上升。'),
('慢跑', 7.0, '轻松的跑步，可以边跑边交谈。'),
('跑步 (中速)', 9.8, '以稳定的中等速度跑步。'),
('跑步 (快速)', 11.0, '以较快的速度进行跑步训练。'),
('游泳 (自由泳, 慢速)', 7.0, '以放松的速度进行自由泳。'),
('游泳 (蛙泳)', 10.0, '以正常速度进行蛙泳。'),
('自行车 (休闲)', 4.0, '悠闲地骑自行车，例如在公园。'),
('自行车 (中速)', 8.0, '以中等强度骑行，用于锻炼。'),
('跳绳', 10.0, '中等速度的跳绳。'),
('力量训练 (一般)', 3.5, '一般的举重或力量训练。'),
('高强度间歇训练 (HIIT)', 8.0, '例如 Tabata 或其他高强度间歇性训练。'),
('瑜伽', 2.5, '哈他瑜伽等常规瑜伽练习。');

-- 索引创建 (为了提高查询效率)
CREATE INDEX idx_user_food_log_user_date ON user_food_log(user_id, log_date);
CREATE INDEX idx_user_exercise_log_user_date ON user_exercise_log(user_id, log_date);
CREATE INDEX idx_foods_description ON foods(description);