
# Nutri-Plan: 个人饮食运动热量收支平衡系统 - 技术文档

## 1. 项目概述

本文档提供了 Nutri-Plan 应用的详细技术说明，这是一个个人饮食运动热量收支平衡系统。该系统旨在帮助用户跟踪他们的日常食物摄入和运动，计算他们的热量收支，并获得个性化的饮食和运动建议，以实现他们的健康目标（减肥、增肌或维持）。

该应用由三个主要部分组成：一个 **Vue.js 前端**，一个 **FastAPI 后端**，以及一个 **MySQL 数据库**。

## 2. 系统架构

该系统遵循经典的客户端-服务器架构：

```
+---------------------+      +-----------------------+      +---------------------+
|      前端 (Frontend)      |      |        后端 (Backend)         |      |      数据库 (Database)      |
| (Vue.js, ElementUI) |      | (FastAPI, Python)     |      |      (MySQL)        |
+---------------------+      +-----------------------+      +---------------------+
| - 用户界面 (User Interface)    |      | - API 接口 (API Endpoints)       |      | - 用户表 (users)             |
| - 基于组件 (Component-based)   |      | - 业务逻辑 (Business Logic)      |      | - 食物表 (foods)             |
| - API 客户端 (API Client)        |      | - 服务 (Services)            |      | - 运动表 (exercises)         |
+---------------------+      | - CRUD 层 (CRUD Layer)          |      | - 用户食物日志 (user_food_log)     |
        |              |      | - 认证 (Authentication)      |      | - 用户运动日志 (user_exercise_log) |
        | HTTP 请求 (HTTP Requests)|      | - 数据验证 (Data Validation)     |      |                     |
        | (REST API)   |      +-----------------------+      +---------------------+
        v              v              |
+---------------------+      +-----------------------+
|   用户浏览器 (User's Browser)    |      |    USDA 食物数据 (USDA Food Data)     |
+---------------------+      |    (CSV 文件)        |
                             +-----------------------+
                                     |
                                     | 数据导入 (Data Import)
                                     v
                             +-----------------------+
                             |  Python 导入脚本 (Python Import Script) |
                             +-----------------------+
```

- **前端**: 一个使用 Vue.js 和 ElementPlus UI 库构建的单页应用 (SPA)。它为所有用户交互提供了一个用户友好的界面。
- **后端**: 一个使用 FastAPI 构建的 RESTful API。它处理所有业务逻辑、数据处理以及与数据库的通信。
- **数据库**: 一个 MySQL 数据库，用于存储所有应用数据，包括用户信息、食物数据和运动日志。

---

## 3. 后端 (FastAPI)

### 3.1. 项目结构

后端代码被组织成一个模块化结构，以促进关注点分离和可维护性。

```
backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   ├── router.py
│   │   │   └── endpoints/
│   │   │       ├── users.py
│   │   │       ├── foods.py
│   │   │       ├── exercises.py
│   │   │       ├── tracking.py
│   │   │       └── recommendations.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── crud/
│   │   │   ├── crud_user.py
│   │   │   ├── crud_food.py
│   │   │   └── crud_log.py
│   │   ├── db/
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── food.py
│   │   │   ├── exercise.py
│   │   │   └── log.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── token.py
│   │   │   ├── food.py
│   │   │   ├── exercise.py
│   │   │   └── log.py
│   │   ├── services/
│   │   │   ├── calorie_calculator.py
│   │   │   ├── recommendation_service.py
│   │   │   ├── menu_generator.py
│   │   │   └── tracking_service.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
```

- **`api/`**: 包含 API 接口、路由和依赖项。
- **`core/`**: 包含核心应用设置和安全相关功能。
- **`crud/`**: 包含数据库的创建、读取、更新和删除 (CRUD) 操作的功能。
- **`db/`**: 包含数据库会话管理。
- **`models/`**: 包含 SQLAlchemy 数据库模型。
- **`schemas/`**: 包含用于数据验证和序列化的 Pydantic 模式。
- **`services/`**: 包含应用的业务逻辑。
- **`main.py`**: FastAPI 应用的入口点。

### 3.2. 配置和依赖

- **`.env`**: 此文件存储环境变量，例如数据库连接详细信息和密钥。它应该在 `backend` 目录中创建。
- **`requirements.txt`**: 此文件列出了后端所需的所有 Python 依赖项。可以使用 `pip install -r requirements.txt` 来安装它们。

### 3.3. 主应用 (`main.py`)

此文件初始化 FastAPI 应用，配置 CORS 中间件，并包含主 API 路由。

### 3.4. API 接口

API 根据功能分为几个模块。所有接口都受 JWT 身份验证保护。

#### 用户 (`/api/users`)

- **`POST /register`**: 注册一个新用户。
- **`POST /login/token`**: 对用户进行身份验证并返回一个 JWT。
- **`GET /me`**: 检索当前已验证用户的个人资料。
- **`PUT /me`**: 更新当前已验证用户的个人资料。

#### 食物 (`/api/foods`)

- **`GET /`**: 按关键字搜索食物。

#### 运动 (`/api/exercises`)

- **`GET /`**: 检索所有可用运动的列表。

#### 跟踪 (`/api/tracking`)

- **`POST /food-log/`**: 为当前用户记录食物摄入。
- **`POST /exercise-log/`**: 为当前用户记录运动活动。
- **`GET /daily-summary/`**: 检索特定日期的卡路里摄入和消耗摘要。

#### 推荐 (`/api/recommendations`)

- **`GET /`**: 根据用户的个人资料和目标生成 AI 驱动的菜单建议。

### 3.5. 服务

- **`calorie_calculator.py`**: 根据用户数据计算基础代谢率 (BMR) 和总日能量消耗 (TDEE)。
- **`recommendation_service.py`**: 根据用户的目标提供每日卡路里和宏量营养素摄入的建议。
- **`menu_generator.py`**: 根据推荐的卡路里和宏量营养素摄入量生成每日菜单样本。
- **`tracking_service.py`**: 包含计算每日摘要的业务逻辑。

### 3.6. CRUD 层

CRUD 层提供了一种简单一致的方式来与数据库交互。每个模型都有一个对应的 CRUD 文件，其中包含用于创建、读取、更新和删除记录的功能。

### 3.7. 如何运行

1.  导航到 `backend` 目录。
2.  使用您的数据库凭据创建一个 `.env` 文件。
3.  安装依赖项: `pip install -r requirements.txt`
4.  启动开发服务器: `uvicorn app.main:app --reload`

---

## 4. 前端 (Vue.js)

### 4.1. 项目结构

前端是使用 Vite 创建的 Vue.js 应用。

```
frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── router/
│       │   └── index.js
│       ├── services/
│       │   └── api.js
│       └── views/
│           ├── Home.vue
│           ├── Register.vue
│           ├── Login.vue
│           ├── FoodTracker.vue
│           ├── ExerciseTracker.vue
│           ├── DailySummary.vue
│           └── MenuSuggestion.vue
```

- **`src/`**: 包含应用的主要源代码。
- **`App.vue`**: 根 Vue 组件。
- **`main.js`**: Vue 应用的入口点。
- **`router/`**: 包含路由配置。
- **`services/`**: 包含用于与后端通信的 API 服务。
- **`views/`**: 包含应用的不同页面。

### 4.2. 配置和依赖

- **`package.json`**: 此文件列出了前端所需的所有 JavaScript 依赖项。可以使用 `npm install` 来安装它们。
- **`vite.config.js`**: Vite 开发服务器和构建过程的配置文件。

### 4.3. 主应用 (`main.js`)

此文件初始化 Vue 应用、Vue Router 和 ElementPlus UI 库。

### 4.4. 组件和视图

- **`Home.vue`**: 应用的登录页面。
- **`Register.vue`**: 新用户注册的表单。
- **`Login.vue`**: 用户登录的表单。
- **`FoodTracker.vue`**: 用于搜索食物和记录食物摄入的页面。
- **`ExerciseTracker.vue`**: 用于记录运动活动的页面。
- **`DailySummary.vue`**: 显示用户每日卡路里平衡摘要的页面。
- **`MenuSuggestion.vue`**: 显示 AI 驱动的菜单建议的页面。

### 4.5. API 服务 (`api.js`)

此文件使用 `axios` 库集中管理所有对后端的 API 调用。它还包括一个拦截器，可自动将 JWT 添加到每个请求的授权头中。

### 4.6. 如何运行

1.  导航到 `frontend` 目录。
2.  安装依赖项: `npm install`
3.  启动开发服务器: `npm run dev`

---

## 5. 数据库 (MySQL)

### 5.1. 模式 (`database/nutri_plan.sql`)

数据库模式在此 SQL 文件中定义。它创建了以下表：

- **`users`**: 存储用户信息。
- **`foods`**: 存储食物和营养数据。
- **`exercises`**: 存储运动信息。
- **`user_food_log`**: 记录用户的食物摄入。
- **`user_exercise_log`**: 记录用户的运动活动。

这些表使用逻辑外键（即存储相关记录的 ID）而不是物理外键约束。

### 5.2. 数据导入 (`database/import_usda_data.py`)

此 Python 脚本用于将来自 USDA FoodData Central CSV 文件的食物数据导入到 `foods` 表中。该脚本读取 CSV 文件，处理数据，并将其插入数据库，同时避免重复。

### 5.3. 如何设置

1.  确保您正在运行 MySQL 服务器。
2.  创建一个新数据库 (例如, `nutri_plan`)。
3.  执行 `database/nutri_plan.sql` 脚本以创建表。
4.  运行 `database/import_usda_data.py` 脚本以填充 `foods` 表。
