# 数据库模块说明

## 概述

我们已经在 `backend/app/db/` 目录下创建了完整的Supabase数据库操作模块，包含以下文件：

- `client.py` - Supabase客户端初始化和连接管理
- `models.py` - 数据模型定义和字段常量
- `crud.py` - 数据库增删改查操作
- `__init__.py` - 模块导出

## 文件结构

```
backend/app/db/
├── __init__.py          # 模块导出
├── client.py            # 数据库客户端
├── models.py            # 数据模型
└── crud.py              # CRUD操作
```

## 功能特性

### 1. 数据库连接管理 (`client.py`)

- **SupabaseClient类**: 管理PostgreSQL连接池
- **连接方法**: `connect()`, `close()`, `test_connection()`
- **查询方法**: `execute()`, `fetch()`, `fetchrow()`, `fetchval()`
- **全局实例**: `db_client` 供整个应用使用

### 2. 数据模型定义 (`models.py`)

#### 表名和字段常量
- `TableNames`: 数据库表名常量
- `UserFields`, `ProjectFields`, `SourceTextFields`, `CharacterFields`: 字段名常量

#### 数据模型类
- **User**: 用户模型
- **Project**: 项目模型  
- **SourceText**: 原文模型
- **Character**: 角色模型
- **Storyboard**: 分镜模型
- **StoryboardPage**: 分镜页面模型
- **StoryboardPanel**: 分镜面板模型

#### 枚举类型
- **ProjectVisibility**: 项目可见性枚举 (private/public)

### 3. CRUD操作 (`crud.py`)

#### 用户操作
- `create_user()` - 创建用户
- `get_user_by_id()` - 根据ID获取用户
- `get_user_by_username()` - 根据用户名获取用户
- `get_user_by_email()` - 根据邮箱获取用户
- `update_user_credit()` - 更新用户积分

#### 项目操作
- `create_project()` - 创建项目
- `get_project_by_id()` - 根据ID获取项目
- `get_projects_by_user()` - 获取用户的所有项目
- `update_project()` - 更新项目信息
- `delete_project()` - 删除项目

#### 原文操作
- `create_source_text()` - 创建原文记录
- `get_source_texts_by_project()` - 获取项目的所有原文
- `save_storyboard()` - 保存分镜数据
- `load_storyboard()` - 加载分镜数据

#### 角色操作
- `create_character()` - 创建角色
- `get_characters_by_project()` - 获取项目的所有角色
- `update_character()` - 更新角色信息
- `delete_character()` - 删除角色

#### 公共查询
- `get_public_projects()` - 获取公开项目列表
- `search_projects()` - 搜索项目
- `get_user_stats()` - 获取用户统计信息

## API接口更新

### 新增接口

1. **POST /api/v1/save-storyboard** - 保存分镜数据
2. **POST /api/v1/create-project** - 创建新项目
3. **GET /api/v1/projects/{user_id}** - 获取用户项目列表
4. **GET /api/v1/project/{project_id}** - 获取项目详情
5. **GET /api/v1/public-projects** - 获取公开项目列表

### 更新接口

- **POST /api/v1/parse** - 增加了自动保存分镜到数据库的功能

## 数据库表结构

基于你提供的Supabase表结构：

### users表
- `user_id` (UUID, 主键)
- `username` (VARCHAR, 唯一)
- `email` (VARCHAR, 唯一)
- `hashed_password` (VARCHAR)
- `credit_balance` (INT, 默认0)
- `created_at`, `updated_at` (TIMESTAMP)

### projects表
- `project_id` (UUID, 主键)
- `user_id` (UUID, 外键)
- `title` (VARCHAR)
- `description` (TEXT)
- `visibility` (ENUM: private/public)
- `default_style_prompt` (TEXT)
- `created_at`, `updated_at` (TIMESTAMP)

### source_texts表
- `text_id` (UUID, 主键)
- `project_id` (UUID, 外键)
- `title` (VARCHAR)
- `raw_content` (TEXT)
- `order_index` (INT)
- `created_at` (TIMESTAMP)

### characters表
- `character_id` (UUID, 主键)
- `project_id` (UUID, 外键)
- `name` (VARCHAR)
- `description` (TEXT)
- `reference_image_urls` (JSON)
- `lora_model_path` (VARCHAR)
- `trigger_word` (VARCHAR)

## 使用方法

### 1. 导入模块
```python
from app.db import (
    init_database, close_database, db_client,
    create_user, get_user_by_username,
    create_project, get_projects_by_user,
    save_storyboard, load_storyboard
)
```

### 2. 初始化数据库
```python
# 在应用启动时
await init_database()

# 检查连接状态
if db_client.is_connected:
    print("数据库已连接")
```

### 3. 使用CRUD操作
```python
# 创建用户
user = await create_user("username", "email@example.com", "hashed_password")

# 创建项目
project = await create_project(user.user_id, "项目标题", "项目描述")

# 保存分镜
storyboard = Storyboard.from_dict({"pages": [...]})
await save_storyboard(project.project_id, storyboard)
```

### 4. 关闭连接
```python
# 在应用关闭时
await close_database()
```

## 测试

运行测试脚本验证数据库连接：

```bash
cd backend
python test_db.py
```

## 配置要求

确保 `backend/config.json` 包含正确的Supabase数据库配置：

```json
{
  "database": {
    "url": "postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres",
    "host": "db.xxx.supabase.co",
    "port": 5432,
    "database": "postgres",
    "username": "postgres",
    "password": "your_password"
  }
}
```

## 注意事项

1. **连接池**: 使用asyncpg连接池，最大10个连接
2. **错误处理**: 所有操作都有异常处理
3. **JSON字段**: 角色参考图片URLs使用JSON存储
4. **分镜存储**: 暂时存储在项目的description字段中（JSON格式）
5. **UUID**: 所有主键和外键使用UUID类型
6. **时区**: 时间戳使用UTC时区

这个数据库模块提供了完整的Supabase操作功能，支持用户管理、项目管理、原文管理、角色管理和分镜管理等功能。
