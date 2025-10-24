# 用户认证功能实现

本项目已成功实现了完整的用户登录注册功能，包括前端和后端的完整实现。

## 🏗️ 架构设计

### 后端架构

```
backend/
├── app/
│   ├── api/
│   │   └── auth.py              # 认证API路由
│   ├── services/
│   │   └── auth_service.py      # 认证服务层
│   ├── db/
│   │   ├── models.py           # 数据模型
│   │   └── crud.py             # 数据库操作
│   └── main.py                 # 主应用入口
├── requirements.txt            # 依赖包
└── test_auth.py               # 认证功能测试
```

### 前端架构

```
frontend/
├── pages/auth/
│   ├── login.vue              # 登录页面
│   └── register.vue          # 注册页面
├── utils/
│   └── auth.js               # 认证管理器
└── config/
    └── index.js              # 配置文件
```

## 🔧 技术栈

### 后端技术
- **FastAPI**: Web框架
- **JWT**: 用户认证令牌
- **bcrypt**: 密码加密
- **python-jose**: JWT处理
- **passlib**: 密码哈希

### 前端技术
- **Vue.js**: 前端框架
- **uni-app**: 跨平台开发框架
- **本地存储**: 令牌和用户信息管理

## 🚀 功能特性

### 用户注册
- ✅ 用户名唯一性验证
- ✅ 邮箱唯一性验证
- ✅ 密码强度验证
- ✅ 自动生成JWT令牌
- ✅ 用户协议确认

### 用户登录
- ✅ 用户名/邮箱登录
- ✅ 密码验证
- ✅ JWT令牌生成
- ✅ 记住我功能
- ✅ 自动跳转

### 安全特性
- ✅ 密码bcrypt加密
- ✅ JWT令牌认证
- ✅ 令牌自动刷新
- ✅ 认证状态管理
- ✅ 登出功能

## 📡 API接口

### 认证接口

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 用户登录 | POST | `/api/v1/auth/login` | 用户登录验证 |
| 用户注册 | POST | `/api/v1/auth/register` | 新用户注册 |
| 获取用户信息 | GET | `/api/v1/auth/me` | 获取当前用户信息 |
| 刷新令牌 | POST | `/api/v1/auth/refresh` | 刷新访问令牌 |
| 用户登出 | POST | `/api/v1/auth/logout` | 用户登出 |
| 健康检查 | GET | `/api/v1/auth/health` | 认证服务状态 |

### 请求示例

#### 登录请求
```json
{
  "username": "testuser",
  "password": "password123"
}
```

#### 注册请求
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123"
}
```

### 响应示例

#### 成功响应
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "user_id": "uuid-string",
    "username": "testuser",
    "email": "user@example.com",
    "credit_balance": 0
  }
}
```

## 🛠️ 安装和运行

### 后端安装

1. 安装依赖包：
```bash
cd backend
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
# 设置JWT密钥
export JWT_SECRET_KEY="your-secret-key-change-in-production"
```

3. 运行服务：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端运行

1. 使用HBuilderX打开frontend目录
2. 运行到浏览器或模拟器
3. 访问登录/注册页面测试功能

## 🧪 测试

### 运行认证功能测试
```bash
cd backend
python test_auth.py
```

### 手动测试步骤

1. **注册测试**：
   - 访问注册页面
   - 输入用户名、邮箱、密码
   - 确认用户协议
   - 点击注册按钮

2. **登录测试**：
   - 访问登录页面
   - 输入用户名/邮箱和密码
   - 点击登录按钮

3. **API测试**：
   - 使用Postman或curl测试API接口
   - 验证令牌有效性
   - 测试受保护的接口

## 🔒 安全注意事项

1. **生产环境配置**：
   - 修改JWT_SECRET_KEY为强密钥
   - 使用HTTPS协议
   - 配置CORS允许的域名

2. **密码安全**：
   - 密码使用bcrypt加密存储
   - 前端不存储明文密码
   - 支持密码强度验证

3. **令牌安全**：
   - JWT令牌有过期时间
   - 支持令牌自动刷新
   - 登出时清除本地存储

## 📝 使用说明

### 前端使用

1. **导入认证管理器**：
```javascript
import authManager from '../../utils/auth.js'
```

2. **用户登录**：
```javascript
const result = await authManager.login(username, password)
if (result.success) {
  // 登录成功，用户信息已自动保存
}
```

3. **用户注册**：
```javascript
const result = await authManager.register(username, email, password)
if (result.success) {
  // 注册成功，用户信息已自动保存
}
```

4. **检查登录状态**：
```javascript
if (authManager.isLoggedIn()) {
  // 用户已登录
}
```

5. **用户登出**：
```javascript
await authManager.logout()
```

### 后端使用

1. **保护API接口**：
```python
from app.api.auth import get_current_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

2. **获取当前用户**：
```python
from app.services.auth_service import auth_service

user = await auth_service.get_current_user(token)
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**：
   - 检查Supabase配置
   - 验证数据库连接字符串

2. **JWT令牌无效**：
   - 检查JWT_SECRET_KEY配置
   - 验证令牌是否过期

3. **前端API调用失败**：
   - 检查API基础URL配置
   - 验证CORS设置

4. **密码验证失败**：
   - 检查密码加密算法
   - 验证密码哈希存储

## 🔄 更新日志

- **v1.0.0**: 初始实现
  - 用户注册功能
  - 用户登录功能
  - JWT令牌认证
  - 前端认证管理器
  - 完整的API接口

## 📞 支持

如有问题或建议，请提交Issue或联系开发团队。


