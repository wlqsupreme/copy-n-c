# backend/app/main.py
#
# FastAPI应用主入口文件
# 
# 这个文件现在变得非常简洁，只负责：
# 1. 应用启动和配置
# 2. 中间件设置（CORS等）
# 3. 路由组装和挂载
# 4. 数据库连接管理
# 5. 健康检查接口
#
# 设计原则：
# - 保持极简，不包含业务逻辑
# - 通过导入和组装其他模块完成功能
# - 便于协作者添加新的API路由
# - 清晰的启动和关闭流程

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 添加 backend 目录到 Python 路径，确保能导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置和数据库模块
from config import config
from app.db import init_database, close_database, db_client

# 导入API路由模块
from app.api import storyboard, project, auth, text_to_image, storyboard_image_gen

# 检查配置是否有效
if not config.is_valid():
    print(config.get_error_message())
    sys.exit(1)

# 创建FastAPI应用实例
app = FastAPI(
    title="小说转漫画API",
    description="基于AI的小说文本解析和分镜生成服务",
    version="1.0.0"
)

# 添加CORS中间件，允许前端跨域访问
# 重要：CORS 中间件必须在路由挂载之前添加，这样所有路由（包括静态文件）都会应用 CORS 头
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境），生产环境应指定具体域名，如 ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 暴露所有响应头，确保前端可以访问
)

# 挂载API路由
# 认证相关的API路由
app.include_router(auth.router)
# 分镜相关的API路由
app.include_router(storyboard.router)
# 项目管理相关的API路由
app.include_router(project.router)
# 文生图相关的API路由
app.include_router(text_to_image.router)
# 分镜图片生成相关的API路由
app.include_router(storyboard_image_gen.router)

# 配置静态文件服务，用于提供生成的图片
# 注意：静态文件路由会自动继承上面配置的 CORS 中间件
# __file__ 是 backend/app/main.py
# dirname(dirname(__file__)) = backend目录
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(backend_root, "layout")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
# 挂载静态文件目录，所有 /layout/* 请求都会从这里提供文件
# CORS 头会自动应用到这些静态文件响应中
app.mount("/layout", StaticFiles(directory=static_dir), name="layout")
print(f"📁 静态文件目录: {static_dir}")
print(f"✅ 静态文件路由已挂载: /layout -> {static_dir}")
print(f"✅ CORS 中间件已配置，静态文件将自动应用 CORS 头")


# ==================== 应用生命周期管理 ====================

@app.on_event("startup")
async def startup_event():
    """
    应用启动时初始化数据库连接
    
    功能说明：
    - 检查数据库配置是否完整
    - 初始化Supabase客户端连接
    - 测试数据库连接是否正常
    - 为后续API调用做准备
    """
    print("🚀 应用启动中...")
    
    if config.is_database_configured():
        print("📊 开始初始化数据库连接...")
        success = await init_database()
        
        if success:
            # 测试数据库连接是否正常
            is_connected = await db_client.test_connection()
            if is_connected:
                print("✅ Supabase数据库连接测试成功")
            else:
                print("❌ Supabase数据库连接测试失败")
        else:
            print("❌ 数据库初始化失败")
    else:
        print("⚠️ 数据库未配置，跳过数据库初始化")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时清理资源
    
    功能说明：
    - 关闭数据库连接
    - 清理相关资源
    - 确保优雅关闭
    """
    print("🛑 应用关闭中...")
    await close_database()
    print("✅ 应用已安全关闭")


# ==================== 基础健康检查接口 ====================

@app.get("/health")
async def health():
    """
    健康检查接口
    
    功能说明：
    - 用于监控系统状态
    - 负载均衡器健康检查
    - 简单的系统可用性验证
    
    返回：
        dict: 包含系统状态的JSON响应
    """
    return {"status": "ok", "message": "服务正常运行"}


# ==================== 应用信息接口 ====================

@app.get("/")
async def root():
    """
    根路径接口
    
    功能说明：
    - 提供API基本信息
    - 显示可用的API端点
    - 便于开发者了解服务功能
    """
    return {
        "message": "小说转漫画API服务",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
