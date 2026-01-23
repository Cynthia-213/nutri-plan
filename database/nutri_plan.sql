-- 数据库初始化脚本 for Nutri-Plan
-- 包含所有表设计的完整SQL脚本

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
    `gender` ENUM('male', 'female') NOT NULL COMMENT '性别',
    `birthdate` DATE NOT NULL COMMENT '出生日期',
    `height_cm` DECIMAL(5, 2) NOT NULL COMMENT '身高（厘米）',
    `weight_kg` DECIMAL(5, 2) NOT NULL COMMENT '体重（公斤）',
    `body_fat_pct` DECIMAL(4, 2) DEFAULT NULL COMMENT '体脂率（百分比）',
    `activity_level` ENUM('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active') NOT NULL DEFAULT 'sedentary' COMMENT '日常活动水平',
    `goal` ENUM('maintain', 'lose_weight', 'gain_muscle', 'gain_weight', 'body_recomposition') NOT NULL DEFAULT 'maintain' COMMENT '健康目标',
    `training_experience` ENUM('beginner', 'intermediate', 'advanced') NOT NULL DEFAULT 'beginner' COMMENT '训练经验',
    `last_period_start` DATE DEFAULT NULL COMMENT '上次月经开始日期（仅女性）',
    `enable_periodized_nutrition` VARCHAR(10) NOT NULL DEFAULT 'false' COMMENT '是否启用周期化营养（训练日/休息日）',
    `identity` ENUM('student', 'office_worker', 'flexible', 'fitness_pro', 'health_care') NOT NULL DEFAULT 'office_worker' COMMENT '用户身份分类',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_username (`username`),
    INDEX idx_users_email (`email`)
) COMMENT='用户信息表';

--
-- 食物表 (foods)
-- 存储食物的营养信息
--
DROP TABLE IF EXISTS `foods`;
CREATE TABLE IF NOT EXISTS `foods` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `description_zh` VARCHAR(255) COMMENT '中文食物名称或描述',
    `description_en` VARCHAR(255) COMMENT '英文食物名称或描述',
    `energy_kcal` DECIMAL(10, 2) COMMENT '每100克所含热量（千卡）',
    `protein_g` DECIMAL(10, 2) COMMENT '每100克所含蛋白质（克）',
    `is_high_protein` BOOLEAN DEFAULT FALSE COMMENT '是否高蛋白（蛋白供能比>20%）',
    `fat_g` DECIMAL(10, 2) COMMENT '每100克所含脂肪（克）',
    `is_low_fat` BOOLEAN DEFAULT FALSE COMMENT '是否低脂（脂肪供能比<15%）',
    `carbohydrate_g` DECIMAL(10, 2) COMMENT '每100克所含碳水化合物（克）',
    `is_low_carb` BOOLEAN DEFAULT FALSE COMMENT '是否低碳水（每100g碳水<10g）',
    `fiber_total_dietary_g` DECIMAL(10, 2) COMMENT '每100克所含膳食纤维（克）',
    `is_high_fiber` BOOLEAN DEFAULT FALSE COMMENT '是否高纤维（每100g膳食纤维>3g）',
    `sugars_g` DECIMAL(10, 2) COMMENT '每100克所含糖（克）',
    `fe_mg` DECIMAL(10, 2) COMMENT '每100克所含铁（毫克）',
    `na_mg` DECIMAL(10, 2) COMMENT '每100克所含钠（毫克）',
    `serving_size_g` DECIMAL(10, 2) DEFAULT 100.00 COMMENT '常见份量（克）',
    `source` VARCHAR(100) COMMENT '数据来源',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_foods_description_zh (`description_zh`)
) COMMENT='食物营养信息表';

--
-- 用户禁止食物表 (user_banned_foods)
-- 存储用户禁止的食物列表，在生成菜单时排除这些食物
--
DROP TABLE IF EXISTS `user_banned_foods`;
CREATE TABLE IF NOT EXISTS `user_banned_foods` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID，关联 users.id',
    `food_id` BIGINT NOT NULL COMMENT '禁止的食物ID，关联 foods.id',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_banned_foods_user (`user_id`),
    INDEX idx_banned_foods_food (`food_id`),
    UNIQUE KEY uq_user_banned_food (`user_id`, `food_id`) COMMENT '每个用户对每个食物只能禁止一次',
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`food_id`) REFERENCES `foods`(`id`) ON DELETE CASCADE
) COMMENT='用户禁止食物表';

--
-- 运动表 (exercises)
-- 存储运动项目及其代谢当量（MET, Metabolic Equivalent of Task）
-- MET值是计算运动消耗热量的关键系数
--
DROP TABLE IF EXISTS `exercises`;
CREATE TABLE IF NOT EXISTS `exercises` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL UNIQUE COMMENT '运动名称',
    `met_value` DECIMAL(4, 2) NOT NULL COMMENT '代谢当量(MET)',
    `description` TEXT COMMENT '运动描述',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_exercises_name (`name`)
) COMMENT='运动热量消耗系数表';

--
-- 用户饮食记录表 (user_food_log)
-- 记录用户每日摄入的食物
--
DROP TABLE IF EXISTS `user_food_log`;
CREATE TABLE IF NOT EXISTS `user_food_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID，关联 users.id',
    `food_id` BIGINT NOT NULL COMMENT '食物ID，关联 foods.id',
    `serving_grams` DECIMAL(10, 2) NOT NULL COMMENT '摄入份量（克）',
    `meal_type` ENUM('breakfast', 'lunch', 'dinner', 'snack') NOT NULL COMMENT '餐别',
    `total_calories` DECIMAL(8, 2) DEFAULT NULL COMMENT '预计算总热量（千卡）',
    `log_date` DATE NOT NULL COMMENT '记录日期',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_food_log_user_date (`user_id`, `log_date`),
    INDEX idx_user_food_log_food (`food_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`food_id`) REFERENCES `foods`(`id`) ON DELETE CASCADE
) COMMENT='用户每日饮食记录表';

--
-- 用户运动记录表 (user_exercise_log)
-- 记录用户每日的运动活动
--
DROP TABLE IF EXISTS `user_exercise_log`;
CREATE TABLE IF NOT EXISTS `user_exercise_log` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID，关联 users.id',
    `exercise_id` INT NOT NULL COMMENT '运动ID，关联 exercises.id',
    `duration_minutes` INT NOT NULL COMMENT '运动时长（分钟）',
    `calories_burned` DECIMAL(7, 2) NOT NULL COMMENT '消耗热量（千卡）',
    `log_date` DATE NOT NULL COMMENT '记录日期',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_exercise_log_user_date (`user_id`, `log_date`),
    INDEX idx_user_exercise_log_exercise (`exercise_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`exercise_id`) REFERENCES `exercises`(`id`) ON DELETE CASCADE
) COMMENT='用户每日运动记录表';

--
-- 身体指标记录表 (body_metrics)
-- 用于记录体重、体脂率等指标的变化历史
--
DROP TABLE IF EXISTS `body_metrics`;
CREATE TABLE IF NOT EXISTS `body_metrics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID',
    `record_date` DATE NOT NULL COMMENT '记录日期',
    `weight_kg` DECIMAL(5, 2) COMMENT '体重（公斤）',
    `body_fat_pct` DECIMAL(4, 2) COMMENT '体脂率（百分比）',
    `muscle_mass_kg` DECIMAL(5, 2) COMMENT '肌肉量（公斤，可选）',
    `notes` TEXT COMMENT '备注',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_body_metrics_user_date (`user_id`, `record_date`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) COMMENT='用户身体指标历史记录表';

--
-- 推荐调整历史表 (recommendation_adjustments)
-- 记录每次推荐调整的详细信息
--
DROP TABLE IF EXISTS `recommendation_adjustments`;
CREATE TABLE IF NOT EXISTS `recommendation_adjustments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID',
    `adjustment_date` DATE NOT NULL COMMENT '调整日期',
    `previous_kcal` DECIMAL(8, 2) COMMENT '调整前热量',
    `new_kcal` DECIMAL(8, 2) COMMENT '调整后热量',
    `previous_protein_g` DECIMAL(6, 2) COMMENT '调整前蛋白质（克）',
    `new_protein_g` DECIMAL(6, 2) COMMENT '调整后蛋白质（克）',
    `previous_fat_g` DECIMAL(6, 2) COMMENT '调整前脂肪（克）',
    `new_fat_g` DECIMAL(6, 2) COMMENT '调整后脂肪（克）',
    `previous_carbs_g` DECIMAL(6, 2) COMMENT '调整前碳水化合物（克）',
    `new_carbs_g` DECIMAL(6, 2) COMMENT '调整后碳水化合物（克）',
    `adjustment_reason` TEXT COMMENT '调整原因',
    `trigger_factors` JSON COMMENT '触发调整的因素（JSON格式）',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_recommendation_adjustments_user_date (`user_id`, `adjustment_date`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) COMMENT='推荐调整历史记录表';

--
-- 社区动态表 (blogs)
-- 存储用户发布的社区动态
--
DROP TABLE IF EXISTS `blog_likes`;
DROP TABLE IF EXISTS `blog_images`;
DROP TABLE IF EXISTS `blog_comments`;
DROP TABLE IF EXISTS `blogs`;

CREATE TABLE IF NOT EXISTS `blogs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '发布者ID',
    `title` VARCHAR(100) NOT NULL COMMENT '动态标题',
    `content` TEXT NOT NULL COMMENT '正文内容',
    `likes_count` INT DEFAULT 0 COMMENT '点赞数',
    `is_public` BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否公开',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_blogs_user (`user_id`),
    INDEX idx_blogs_created (`created_at`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) COMMENT='社区动态表';

--
-- 博客图片表 (blog_images)
-- 存储博客关联的图片
--
CREATE TABLE IF NOT EXISTS `blog_images` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `blog_id` INT NOT NULL COMMENT '博客ID，关联 blogs.id',
    `image_url` VARCHAR(500) NOT NULL COMMENT '图片URL',
    `sort_order` INT DEFAULT 0 COMMENT '排序顺序（0-8，最多9张）',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_blog_images_blog (`blog_id`),
    FOREIGN KEY (`blog_id`) REFERENCES `blogs`(`id`) ON DELETE CASCADE
) COMMENT='博客图片表';

--
-- 社区评论表 (blog_comments)
-- 存储博客的评论和回复
--
CREATE TABLE IF NOT EXISTS `blog_comments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `blog_id` INT NOT NULL COMMENT '关联博客ID',
    `user_id` INT NOT NULL COMMENT '评论用户ID',
    `content` TEXT NOT NULL COMMENT '评论内容',
    `parent_id` INT DEFAULT NULL COMMENT '父评论ID，用于二级回复',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_comments_blog (`blog_id`),
    INDEX idx_comments_parent (`parent_id`),
    INDEX idx_comments_user (`user_id`),
    FOREIGN KEY (`blog_id`) REFERENCES `blogs`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`parent_id`) REFERENCES `blog_comments`(`id`) ON DELETE CASCADE
) COMMENT='社区评论表';

--
-- 博客点赞表 (blog_likes)
-- 存储用户对博客的点赞记录
--
CREATE TABLE IF NOT EXISTS `blog_likes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `blog_id` INT NOT NULL COMMENT '关联博客ID',
    `user_id` INT NOT NULL COMMENT '点赞用户ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_likes_blog (`blog_id`),
    INDEX idx_likes_user (`user_id`),
    UNIQUE KEY uk_blog_user (`blog_id`, `user_id`) COMMENT '每个用户对每条博客只能点赞一次',
    FOREIGN KEY (`blog_id`) REFERENCES `blogs`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) COMMENT='博客点赞表';

--
-- 通知表 (notifications)
-- 存储用户收到的通知
--
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE IF NOT EXISTS `notifications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '接收通知的用户ID',
    `type` ENUM('like', 'comment', 'reply') NOT NULL COMMENT '通知类型',
    `blog_id` INT DEFAULT NULL COMMENT '关联的博客ID',
    `comment_id` INT DEFAULT NULL COMMENT '关联的评论ID',
    `from_user_id` INT NOT NULL COMMENT '触发通知的用户ID',
    `content` TEXT COMMENT '通知内容（如评论内容预览）',
    `is_read` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已读',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_notifications_user (`user_id`),
    INDEX idx_notifications_blog (`blog_id`),
    INDEX idx_notifications_comment (`comment_id`),
    INDEX idx_notifications_created (`created_at`),
    INDEX idx_notifications_read (`is_read`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`from_user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`blog_id`) REFERENCES `blogs`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`comment_id`) REFERENCES `blog_comments`(`id`) ON DELETE CASCADE
) COMMENT='通知表';

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

--
-- 触发器：自动更新食物标签字段
-- 当食物数据更新时，自动计算并更新 is_high_protein, is_low_carb, is_low_fat, is_high_fiber 字段
--
DELIMITER $$

CREATE TRIGGER `update_food_labels_before_insert` 
BEFORE INSERT ON `foods`
FOR EACH ROW
BEGIN
    SET NEW.is_high_protein = IF(NEW.energy_kcal > 0 AND (NEW.protein_g * 4.0 / NEW.energy_kcal) > 0.2, TRUE, FALSE);
    SET NEW.is_low_carb = IF(NEW.carbohydrate_g < 10, TRUE, FALSE);
    SET NEW.is_low_fat = IF(NEW.energy_kcal > 0 AND (NEW.fat_g * 9.0 / NEW.energy_kcal) < 0.15, TRUE, FALSE);
    SET NEW.is_high_fiber = IF(NEW.fiber_total_dietary_g > 3, TRUE, FALSE);
END$$

CREATE TRIGGER `update_food_labels_before_update` 
BEFORE UPDATE ON `foods`
FOR EACH ROW
BEGIN
    SET NEW.is_high_protein = IF(NEW.energy_kcal > 0 AND (NEW.protein_g * 4.0 / NEW.energy_kcal) > 0.2, TRUE, FALSE);
    SET NEW.is_low_carb = IF(NEW.carbohydrate_g < 10, TRUE, FALSE);
    SET NEW.is_low_fat = IF(NEW.energy_kcal > 0 AND (NEW.fat_g * 9.0 / NEW.energy_kcal) < 0.15, TRUE, FALSE);
    SET NEW.is_high_fiber = IF(NEW.fiber_total_dietary_g > 3, TRUE, FALSE);
END$$

DELIMITER ;
