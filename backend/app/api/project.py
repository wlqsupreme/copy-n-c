# backend/app/api/project.py
#
# 项目管理相关的API路由
# 
# 这个文件专门负责：
# 1. 接收前端Vue页面的项目管理请求
# 2. 处理项目的创建、查询、更新、删除操作
# 3. 管理项目的可见性和权限
# 4. 加载项目相关的分镜数据
#
# 设计原则：
# - 只处理HTTP请求/响应，不包含业务逻辑
# - 通过调用db层完成数据库操作
# - 统一的错误处理和状态码返回
# - 为前端提供完整的项目管理接口

from fastapi import APIRouter, HTTPException
from typing import List
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入数据库层
from app.db import (
    db_client, create_project, get_projects_by_user,
    get_project_by_id, get_public_projects,
    ProjectVisibility
)

# 创建项目管理相关的路由器
router = APIRouter()

# ==================== API接口定义 ====================

@router.post("/api/v1/create-project", tags=["Project"])
async def create_project_endpoint(
    user_id: str,
    title: str,
    description: str | None = None,
    visibility: str = "private"
):
    """
    创建新项目
    
    功能说明：
    - 为用户创建新的小说转漫画项目
    - 设置项目标题、描述和可见性
    - 在数据库中创建项目记录
    - 返回创建的项目信息
    
    使用场景：
    - 用户开始新的小说转漫画项目
    - 项目初始化设置
    - 项目元数据管理
    
    参数：
        user_id: 用户ID（必需）
        title: 项目标题（必需）
        description: 项目描述（可选）
        visibility: 项目可见性（private/public，默认private）
    
    返回：
        dict: 包含项目信息的JSON响应
    """
    print(f"📁(API) 收到创建项目请求:")
    print(f"   用户ID: {user_id}")
    print(f"   标题: {title}")
    print(f"   描述: {description}")
    print(f"   可见性: {visibility}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 1. 验证可见性参数
        try:
            vis_enum = ProjectVisibility(visibility)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的可见性设置，必须是 'private' 或 'public'")
        
        # 2. 创建项目
        project = await create_project(
            user_id=user_id,
            title=title,
            description=description,
            visibility=vis_enum
        )
        
        if project:
            print(f"✅(API) 项目创建成功: {project.project_id}")
            return {"ok": True, "project": project.to_dict()}
        else:
            print(f"❌(API) 项目创建失败")
            raise HTTPException(status_code=500, detail="项目创建失败")
            
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"❌(API) 创建项目失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")


@router.get("/api/v1/projects/{user_id}", tags=["Project"])
async def get_user_projects(user_id: str):
    """
    获取用户的项目列表
    
    功能说明：
    - 查询指定用户的所有项目
    - 返回项目的基本信息列表
    - 支持分页和排序（可扩展）
    
    使用场景：
    - 用户查看自己的项目列表
    - 项目管理和选择
    - 用户工作台展示
    
    参数：
        user_id: 用户ID
    
    返回：
        dict: 包含项目列表的JSON响应
    """
    print(f"📋(API) 收到获取用户项目请求: {user_id}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 查询用户项目
        projects = await get_projects_by_user(user_id)
        
        print(f"✅(API) 获取用户项目成功，共 {len(projects)} 个项目")
        return {"ok": True, "projects": [project.to_dict() for project in projects]}
        
    except Exception as e:
        print(f"❌(API) 获取用户项目失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取项目失败: {str(e)}")


@router.get("/api/v1/project/{project_id}", tags=["Project"])
async def get_project(project_id: str):
    """
    获取项目详情
    
    功能说明：
    - 根据项目ID获取项目基本信息
    - 不再包含分镜数据（分镜数据通过专门的API获取）
    - 返回项目基本信息
    
    使用场景：
    - 用户打开项目进行编辑
    - 项目详情页面展示
    - 项目基本信息显示
    
    参数：
        project_id: 项目ID
    
    返回：
        dict: 包含项目详情的JSON响应
    """
    print(f"📂(API) 收到获取项目详情请求: {project_id}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 1. 获取项目基本信息
        project = await get_project_by_id(project_id)
        if not project:
            print(f"❌(API) 项目不存在: {project_id}")
            raise HTTPException(status_code=404, detail="项目不存在")
        
        # 2. 组装返回数据
        result = project.to_dict()
        print(f"✅(API) 项目详情加载成功")
        
        return {"ok": True, "project": result}
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"❌(API) 获取项目失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取项目失败: {str(e)}")


@router.get("/api/v1/public-projects", tags=["Project"])
async def get_public_projects_endpoint(limit: int = 20, offset: int = 0):
    """
    获取公开项目列表
    
    功能说明：
    - 查询所有设置为公开的项目
    - 支持分页查询（limit和offset）
    - 用于展示社区作品和灵感
    
    使用场景：
    - 社区作品展示页面
    - 公开项目浏览
    - 灵感来源和参考
    
    参数：
        limit: 每页数量（默认20）
        offset: 偏移量（默认0）
    
    返回：
        dict: 包含公开项目列表的JSON响应
    """
    print(f"🌐(API) 收到获取公开项目请求:")
    print(f"   limit: {limit}")
    print(f"   offset: {offset}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 查询公开项目
        projects = await get_public_projects(limit=limit, offset=offset)
        
        print(f"✅(API) 获取公开项目成功，共 {len(projects)} 个项目")
        return {"ok": True, "projects": [project.to_dict() for project in projects]}
        
    except Exception as e:
        print(f"❌(API) 获取公开项目失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取公开项目失败: {str(e)}")
