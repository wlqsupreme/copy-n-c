# 小说转漫画应用

## 议题说明

**议题一** 开发一个根据一篇小说生成相应漫画的应用。

请回答:
1. 你计划将这个产品面向什么类型的用户?这些类型的用户他们面临什么样的痛点，你设想的用户故事是什么样呢?
2. 你认为这个产品实现上的挑战是什么，你计划如何应对这些挑战?
3. 你计划采纳哪家公司的哪个模型的AIGC功能?你对比了哪些，你为什么选择用该API?
4. 你对这个产品有哪些未来规划中的功能?你为何觉得这些能力是重要的?

请开发以上应用。要求不能调用第三方的agent能力，只需允许调用LLM、各类AIGC模型和语音TTS能力。
同时针对以上1-4点，请把你的思考整理成文档，作为作品的说明一并提交。

---

## 项目概述

这是一个基于AI技术的小说转漫画应用，通过智能文本解析和分镜规划，将小说文本转化为结构化的漫画分镜脚本。项目采用前后端分离架构，后端使用FastAPI + PostgreSQL，前端使用uni-app框架。

## 技术架构

### 后端技术栈
- **框架**: FastAPI 0.115.0
- **数据库**: PostgreSQL (通过Supabase托管)
- **异步数据库驱动**: asyncpg 0.29.0
- **HTTP客户端**: httpx 0.28.0
- **数据验证**: pydantic 2.10.0
- **服务器**: uvicorn 0.32.0

### 前端技术栈
- **框架**: uni-app (Vue.js)
- **平台**: 支持H5、小程序、App等多端
- **UI**: 自定义组件，响应式设计

### AI服务
- **LLM服务**: 七牛云AI开放平台 (gpt-oss-120b模型)
- **API兼容**: OpenAI兼容接口

## 项目结构

```
novel-to-comic/
├── backend/                 # 后端服务
│   ├── app/
│   │   └── main.py         # FastAPI主应用
│   ├── config.py           # 配置管理
│   ├── database.py        # 数据库管理
│   ├── requirements.txt   # Python依赖
│   ├── config.json.example # 配置文件模板
│   └── venv/              # Python虚拟环境
├── frontend/               # 前端应用
│   ├── pages/
│   │   ├── index/         # 首页
│   │   └── storyboard/    # 分镜相关页面
│   ├── App.vue            # 应用入口
│   ├── pages.json         # 页面配置
│   └── static/            # 静态资源
├── .gitignore             # Git忽略文件
└── README.md              # 项目说明
```

## 环境配置

### Python环境要求
- **Python版本**: 3.11 (推荐)
- **虚拟环境**: venv
- **包管理**: pip

### 环境搭建步骤

1. **安装Python 3.11**
   ```bash
   # 下载并安装Python 3.11
   # 注意：不要勾选"Add to PATH"以避免影响其他项目
   ```

2. **创建虚拟环境**
   ```bash
   cd backend
   py -3.11 -m venv venv
   venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置API密钥**
   
   创建 `backend/config.json` 文件：
   ```json
   {
     "qiniu_api_key": "你的七牛云API密钥",
     "model": "gpt-oss-120b",
     "max_tokens": 4096,
     "temperature": 0.2,
     "timeout": 60,
     "database": {
       "url": "postgresql://postgres:[YOUR_PASSWORD]@db.ihpmirffjziqvkkaplpl.supabase.co:5432/postgres",
       "host": "db.ihpmirffjziqvkkaplpl.supabase.co",
       "port": 5432,
       "database": "postgres",
       "username": "postgres",
       "password": "你的数据库密码"
     }
   }
   ```

5. **启动后端服务**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 数据库设计

项目使用Supabase托管的PostgreSQL数据库，包含以下核心表结构：

### 用户表 (users)
- `user_id`: UUID主键
- `username`: 用户名（唯一）
- `email`: 邮箱（唯一）
- `hashed_password`: 加密密码
- `credit_balance`: 可用额度
- `created_at/updated_at`: 时间戳

### 项目表 (projects)
- `project_id`: UUID主键
- `user_id`: 用户外键
- `title`: 项目标题
- `description`: 项目描述
- `visibility`: 可见性（private/public）
- `default_style_prompt`: 默认风格提示词

### 原文表 (source_texts)
- `text_id`: UUID主键
- `project_id`: 项目外键
- `title`: 章节标题
- `raw_content`: 原始文本内容
- `order_index`: 排序索引

### 角色表 (characters)
- `character_id`: UUID主键
- `project_id`: 项目外键
- `name`: 角色名称
- `description`: 角色描述
- `reference_image_urls`: 参考图片URL（JSON）
- `lora_model_path`: LoRA模型路径
- `trigger_word`: 触发词

## 功能特性

### 已实现功能

1. **智能文本解析**
   - 支持长文本自动分段处理
   - AI驱动的智能分段算法
   - 结构化JSON输出

2. **分镜规划**
   - 可视化分镜编辑界面
   - 支持面板增删改查
   - 镜头角度和情绪设置

3. **用户界面**
   - 响应式设计
   - 登录注册功能（UI已完成）
   - 文件上传支持

### 核心API接口

- `POST /api/v1/parse`: 文本解析接口
  - 输入：小说文本
  - 输出：结构化分镜JSON
  - 支持自动分段和手动处理

- `GET /health`: 健康检查接口

## 技术挑战与解决方案

### 1. 文本到分镜转换
**挑战**: 需要理解剧情节点、镜头构图、节奏
**解决方案**: 
- 分层管线设计
- LLM驱动的智能解析
- 结构化JSON输出格式

### 2. 长文本处理
**挑战**: 上下文保持与分场景切分
**解决方案**:
- AI智能分段算法
- 分段摘要处理
- 逐段生成分镜

### 3. 人物一致性
**挑战**: 人物在不同画面保持相貌、服装
**解决方案**:
- 角色参考图上传
- LoRA模型支持
- 专属embedding机制

### 4. 性能与成本控制
**挑战**: 大模型调用成本
**解决方案**:
- 缓存与去重机制
- 异步队列处理
- 用户额度管理

## 开发进度

### ✅ 已完成
- [x] 后端API框架搭建
- [x] 数据库连接和表结构设计
- [x] 七牛云AI API集成
- [x] 文本解析和分镜生成
- [x] 前端基础界面
- [x] 分镜可视化编辑
- [x] 文件上传功能

### 🚧 开发中
- [ ] 用户认证系统
- [ ] 项目管理系统
- [ ] 图像生成功能
- [ ] 角色一致性处理

### 📋 计划中
- [ ] AI图像生成集成
- [ ] 对话气泡排版
- [ ] 作品导出功能
- [ ] 多语言支持

## 运行说明

### 后端启动
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
cd frontend
# 使用HBuilderX或其他uni-app开发工具
# 或使用命令行工具
```

## 配置说明

### 环境变量
- `QINIU_API_KEY`: 七牛云API密钥
- 数据库连接信息

### 配置文件
- `backend/config.json`: 主要配置文件
- `backend/config.json.example`: 配置模板

## 注意事项

1. **API密钥安全**: 配置文件包含敏感信息，已加入.gitignore
2. **数据库连接**: 使用Supabase托管数据库
3. **Python版本**: 推荐使用Python 3.11以避免依赖冲突
4. **跨域设置**: 后端已配置CORS中间件

## 未来规划

### 短期目标
- 完善用户认证系统
- 集成AI图像生成
- 优化分镜编辑体验

### 长期目标
- 支持多种漫画风格
- 智能角色设计
- 社区分享功能
- 商业化运营

---

*本项目基于AI技术，致力于降低漫画创作门槛，让更多人能够将文字故事转化为视觉作品。*
