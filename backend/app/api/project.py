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

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入数据库层
from app.db import (
    db_client, create_project, get_projects_by_user,
    get_project_by_id, get_public_projects, delete_project,
    update_character, update_source_text,
    ProjectVisibility
)

# 创建项目管理相关的路由器
router = APIRouter()

# ==================== Pydantic模型定义 ====================

class ProjectCreate(BaseModel):
    """项目创建请求模型"""
    title: str
    description: Optional[str] = None
    upload_method: str = "single_chapter"  # single_chapter 或 full_novel
    default_style_prompt: Optional[str] = None
    visibility: str = "private"  # private 或 public
    user_id: Optional[str] = None  # 用户ID（从请求中获取）

class ProjectResponse(BaseModel):
    """项目响应模型"""
    project_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    upload_method: str
    default_style_prompt: Optional[str] = None
    visibility: str
    created_at: str
    updated_at: str

# ==================== API接口定义 ====================

@router.post("/api/v1/projects", tags=["Project"], response_model=ProjectResponse)
async def create_project_rest(project_data: ProjectCreate):
    """
    创建新项目 (RESTful接口)
    
    功能说明：
    - 使用RESTful POST /api/v1/projects 接口创建项目
    - 支持新的字段：upload_method, default_style_prompt
    - 自动生成项目ID
    - 返回完整的项目信息
    
    参数：
        project_data: 项目创建数据（包含user_id）
    
    返回：
        ProjectResponse: 创建的项目信息
    """
    # 获取用户ID
    user_id = project_data.user_id
    if not user_id:
        raise HTTPException(status_code=400, detail="用户ID不能为空")
    
    print(f"📁(API) 收到RESTful创建项目请求:")
    print(f"   用户ID: {user_id}")
    print(f"   标题: {project_data.title}")
    print(f"   描述: {project_data.description}")
    print(f"   上传方式: {project_data.upload_method}")
    print(f"   风格提示词: {project_data.default_style_prompt}")
    print(f"   可见性: {project_data.visibility}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 1. 验证可见性参数
        try:
            vis_enum = ProjectVisibility(project_data.visibility)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的可见性设置，必须是 'private' 或 'public'")
        
        # 2. 验证上传方式
        if project_data.upload_method not in ["single_chapter", "full_novel"]:
            raise HTTPException(status_code=400, detail="无效的上传方式，必须是 'single_chapter' 或 'full_novel'")
        
        # 3. 创建项目
        project = await create_project(
            user_id=user_id,
            title=project_data.title,
            description=project_data.description,
            visibility=vis_enum,
            upload_method=project_data.upload_method,
            default_style_prompt=project_data.default_style_prompt
        )
        
        if project:
            print(f"✅(API) 项目创建成功: {project.project_id}")
            
            # 处理日期字段（可能是datetime对象或字符串）
            def format_date(date_value):
                if not date_value:
                    return ""
                if isinstance(date_value, str):
                    return date_value
                if hasattr(date_value, 'isoformat'):
                    return date_value.isoformat()
                return str(date_value)
            
            return ProjectResponse(
                project_id=project.project_id,
                user_id=project.user_id,
                title=project.title,
                description=project.description,
                upload_method=project.upload_method,  # 使用数据库中的值
                default_style_prompt=project.default_style_prompt,
                visibility=project.visibility.value,
                created_at=format_date(project.created_at),
                updated_at=format_date(project.updated_at)
            )
        else:
            print(f"❌(API) 项目创建失败")
            raise HTTPException(status_code=500, detail="项目创建失败")
            
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"❌(API) 创建项目失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")

@router.get("/api/v1/projects", tags=["Project"])
async def get_projects_rest(user_id: str = None):
    """
    获取用户项目列表 (RESTful接口)
    
    功能说明：
    - 使用RESTful GET /api/v1/projects 接口获取项目列表
    - 返回用户的所有项目
    - 包含项目的基本信息和统计
    
    参数：
        user_id: 用户ID（从查询参数中获取）
    
    返回：
        dict: 包含项目列表的JSON响应
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="用户ID不能为空")
    
    print(f"📋(API) 收到RESTful获取项目请求: {user_id}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 查询用户项目
        projects = await get_projects_by_user(user_id)
        
        # 转换为响应格式
        project_list = []
        
        # 处理日期字段的辅助函数
        def format_date(date_value):
            if not date_value:
                return ""
            if isinstance(date_value, str):
                return date_value
            if hasattr(date_value, 'isoformat'):
                return date_value.isoformat()
            return str(date_value)
        
        for project in projects:
            project_dict = {
                "project_id": project.project_id,
                "user_id": project.user_id,
                "title": project.title,
                "description": project.description,
                "upload_method": project.upload_method,
                "default_style_prompt": project.default_style_prompt,
                "visibility": project.visibility.value if hasattr(project.visibility, 'value') else str(project.visibility),
                "created_at": format_date(project.created_at),
                "updated_at": format_date(project.updated_at),
                "chapter_count": 0,  # 临时值，后续需要统计
                "character_count": 0  # 临时值，后续需要统计
            }
            project_list.append(project_dict)
        
        print(f"✅(API) 获取用户项目成功，共 {len(projects)} 个项目")
        return project_list
        
    except Exception as e:
        print(f"❌(API) 获取用户项目失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取项目失败: {str(e)}")

@router.delete("/api/v1/projects/{project_id}", tags=["Project"])
async def delete_project_rest(project_id: str):
    """
    删除项目 (RESTful接口)
    
    功能说明：
    - 使用RESTful DELETE /api/v1/projects/{project_id} 接口删除项目
    - 级联删除相关的分镜和角色数据
    - 需要权限验证（后续添加）
    
    参数：
        project_id: 项目ID
    
    返回：
        dict: 删除结果
    """
    print(f"🗑️(API) 收到RESTful删除项目请求: {project_id}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 删除项目
        success = await delete_project(project_id)
        
        if success:
            print(f"✅(API) 项目删除成功: {project_id}")
            return {"ok": True, "message": "项目删除成功"}
        else:
            print(f"❌(API) 项目删除失败: {project_id}")
            raise HTTPException(status_code=404, detail="项目不存在或删除失败")
            
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"❌(API) 删除项目失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除项目失败: {str(e)}")

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


@router.get("/api/v1/projects/{project_id}/chapters", tags=["Project"])
async def get_project_chapters(project_id: str):
    """
    获取项目的章节列表（包含分镜数量）
    
    功能说明：
    - 获取项目下的所有章节
    - 返回每个章节的分镜数量
    - 支持按章节编号排序
    
    参数：
        project_id: 项目ID
    
    返回：
        dict: 包含章节列表的JSON响应
    """
    print(f"📚(API) 收到获取项目章节请求: {project_id}")
    
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        from app.db import get_source_texts_by_project, get_storyboards_by_text_id
        
        # 获取项目的所有章节
        chapters = await get_source_texts_by_project(project_id)
        
        # 为每个章节添加分镜数量
        chapter_list = []
        for chapter in chapters:
            # 获取该章节的分镜数量
            storyboards = await get_storyboards_by_text_id(chapter.text_id)
            
            # 格式化日期字段
            def format_date(date_value):
                if not date_value:
                    return ""
                if isinstance(date_value, str):
                    return date_value
                if hasattr(date_value, 'isoformat'):
                    return date_value.isoformat()
                return str(date_value)
            
            chapter_dict = {
                "text_id": chapter.text_id,
                "chapter_number": chapter.chapter_number,
                "chapter_name": chapter.chapter_name or chapter.title,
                "storyboard_count": len(storyboards),
                "processing_status": chapter.processing_status,
                "created_at": format_date(chapter.created_at)
            }
            chapter_list.append(chapter_dict)
        
        # 按 order_index 排序
        chapter_list.sort(key=lambda x: x.get('order_index', 0))
        
        print(f"✅(API) 获取项目章节成功，共 {len(chapter_list)} 个章节")
        return {"ok": True, "chapters": chapter_list}
        
    except Exception as e:
        print(f"❌(API) 获取项目章节失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取项目章节失败: {str(e)}")

@router.get("/api/v1/projects/{project_id}/characters", tags=["Project"])
async def get_project_characters(project_id: str):
    """
    获取项目的角色列表
    
    功能说明：
    - 获取项目下的所有角色
    - 返回角色的描述信息
    
    参数：
        project_id: 项目ID
    
    返回：
        dict: 包含角色列表的JSON响应
    """
    print(f"👥(API) 收到获取项目角色请求: {project_id}")
    
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        from app.db import get_characters_by_project
        
        # 获取项目的所有角色
        characters = await get_characters_by_project(project_id)
        
        # 转换为响应格式
        character_list = []
        for char in characters:
            character_dict = {
                "character_id": char.character_id,
                "name": char.name,
                "description": char.description,
                "reference_image_urls": char.reference_image_urls,
                "lora_model_path": char.lora_model_path,
                "trigger_word": char.trigger_word
            }
            character_list.append(character_dict)
        
        print(f"✅(API) 获取项目角色成功，共 {len(character_list)} 个角色")
        return {"ok": True, "characters": character_list}
        
    except Exception as e:
        print(f"❌(API) 获取项目角色失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取项目角色失败: {str(e)}")

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


class CharacterUpdate(BaseModel):
    """角色更新请求模型"""
    description: Optional[str] = None


@router.put("/api/v1/character/{character_id}", tags=["Project"])
async def update_character_api(character_id: str, updates: CharacterUpdate):
    """
    更新角色描述
    
    功能说明：
    - 更新角色的描述信息
    - 用于编辑角色基础设定
    
    参数：
        character_id: 角色ID
        updates: 更新数据
    
    返回：
        dict: 更新结果
    """
    print(f"✏️(API) 更新角色: {character_id}")
    
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        success = await update_character(
            character_id=character_id,
            description=updates.description
        )
        
        if success:
            print(f"✅ 角色更新成功: {character_id}")
            return {"ok": True, "message": "更新成功"}
        else:
            raise HTTPException(status_code=500, detail="更新失败")
            
    except Exception as e:
        print(f"❌(API) 更新角色失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


class SourceTextUpdate(BaseModel):
    """原文更新请求模型"""
    title: Optional[str] = None
    chapter_number: Optional[int] = None
    chapter_name: Optional[str] = None
    order_index: Optional[int] = None


@router.get("/api/v1/source_texts/{text_id}", tags=["Project"])
async def get_source_text_api(text_id: str):
    """
    获取单个原文信息
    
    功能说明：
    - 根据 text_id 获取章节信息
    - 返回章节编号、名称等基本信息
    
    参数：
        text_id: 原文ID
    
    返回：
        dict: 包含章节信息的JSON响应
    """
    print(f"📖(API) 获取章节信息: {text_id}")
    
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        from app.db import get_source_text_by_id
        
        source_text = await get_source_text_by_id(text_id)
        if not source_text:
            raise HTTPException(status_code=404, detail="章节不存在")
        
        chapter_dict = {
            "text_id": source_text.text_id,
            "chapter_number": source_text.chapter_number,
            "chapter_name": source_text.chapter_name or source_text.title,
            "title": source_text.title
        }
        
        print(f"✅ 获取章节信息成功: {text_id}")
        return {"ok": True, "chapter": chapter_dict}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 获取章节信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取章节信息失败: {str(e)}")


@router.put("/api/v1/source_text/{text_id}", tags=["Project"])
async def update_source_text_api(text_id: str, updates: SourceTextUpdate):
    """
    更新原文信息
    
    功能说明：
    - 更新章节的标题、编号和名称
    - 用于编辑章节信息
    
    参数：
        text_id: 原文ID
        updates: 更新数据
    
    返回：
        dict: 更新结果
    """
    print(f"✏️(API) 更新原文: {text_id}")
    
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        success = await update_source_text(
            text_id=text_id,
            title=updates.title,
            chapter_number=updates.chapter_number,
            chapter_name=updates.chapter_name,
            order_index=updates.order_index
        )
        
        if success:
            print(f"✅ 原文更新成功: {text_id}")
            return {"ok": True, "message": "更新成功"}
        else:
            raise HTTPException(status_code=500, detail="更新失败")
            
    except Exception as e:
        print(f"❌(API) 更新原文失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")
