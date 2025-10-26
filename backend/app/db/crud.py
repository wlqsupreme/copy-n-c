"""
数据库增删改查操作
使用Supabase REST API进行数据操作
"""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from .client import db_client
from .models import (
    User, Project, SourceText, Character, Storyboard, StoryboardPanel,
    TableNames, UserFields, ProjectFields, SourceTextFields, CharacterFields, StoryboardFields,
    ProjectVisibility
)


# ==================== 用户相关操作 ====================

async def create_user(username: str, email: str, hashed_password: str) -> Optional[User]:
    """
    创建新用户
    
    Args:
        username: 用户名
        email: 邮箱
        hashed_password: 加密后的密码
        
    Returns:
        Optional[User]: 创建的用户对象或None
    """
    try:
        user_data = {
            UserFields.USER_ID: str(uuid.uuid4()),
            UserFields.USERNAME: username,
            UserFields.EMAIL: email,
            UserFields.HASHED_PASSWORD: hashed_password,
            UserFields.CREDIT_BALANCE: 0
        }
        
        result = await db_client.insert(TableNames.USERS, user_data)
        if result:
            return User.from_dict(result)
        return None
        
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        return None


async def get_user_by_id(user_id: str) -> Optional[User]:
    """根据ID获取用户"""
    try:
        results = await db_client.select(
            TableNames.USERS, 
            filters={UserFields.USER_ID: user_id}
        )
        if results:
            return User.from_dict(results[0])
        return None
    except Exception as e:
        print(f"❌ 获取用户失败: {e}")
        return None


async def get_user_by_username(username: str) -> Optional[User]:
    """根据用户名获取用户"""
    try:
        results = await db_client.select(
            TableNames.USERS,
            filters={UserFields.USERNAME: username}
        )
        if results:
            return User.from_dict(results[0])
        return None
    except Exception as e:
        print(f"❌ 获取用户失败: {e}")
        return None


async def get_user_by_email(email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    try:
        results = await db_client.select(
            TableNames.USERS,
            filters={UserFields.EMAIL: email}
        )
        if results:
            return User.from_dict(results[0])
        return None
    except Exception as e:
        print(f"❌ 获取用户失败: {e}")
        return None


async def update_user_credit(user_id: str, credit_change: int) -> bool:
    """更新用户积分"""
    try:
        # 先获取当前积分
        user = await get_user_by_id(user_id)
        if not user:
            return False
        
        new_balance = user.credit_balance + credit_change
        await db_client.update(
            TableNames.USERS,
            {UserFields.CREDIT_BALANCE: new_balance},
            {UserFields.USER_ID: user_id}
        )
        return True
    except Exception as e:
        print(f"❌ 更新用户积分失败: {e}")
        return False


# ==================== 项目相关操作 ====================

async def create_project(
    user_id: str, 
    title: str, 
    description: Optional[str] = None,
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE,
    default_style_prompt: Optional[str] = None,
    upload_method: str = "single_chapter"
) -> Optional[Project]:
    """
    创建新项目
    
    Args:
        user_id: 用户ID
        title: 项目标题
        description: 项目描述
        visibility: 可见性
        default_style_prompt: 默认风格提示词
        upload_method: 上传方式 (single_chapter 或 full_novel)
        
    Returns:
        Optional[Project]: 创建的项目对象或None
    """
    try:
        project_data = {
            ProjectFields.PROJECT_ID: str(uuid.uuid4()),
            ProjectFields.USER_ID: user_id,
            ProjectFields.TITLE: title,
            ProjectFields.DESCRIPTION: description,
            ProjectFields.VISIBILITY: visibility.value,
            ProjectFields.DEFAULT_STYLE_PROMPT: default_style_prompt,
            ProjectFields.UPLOAD_METHOD: upload_method
        }
        
        result = await db_client.insert(TableNames.PROJECTS, project_data)
        if result:
            return Project.from_dict(result)
        return None
        
    except Exception as e:
        print(f"❌ 创建项目失败: {e}")
        return None


async def get_project_by_id(project_id: str) -> Optional[Project]:
    """根据ID获取项目"""
    try:
        results = await db_client.select(
            TableNames.PROJECTS,
            filters={ProjectFields.PROJECT_ID: project_id}
        )
        if results:
            return Project.from_dict(results[0])
        return None
    except Exception as e:
        print(f"❌ 获取项目失败: {e}")
        return None


async def get_projects_by_user(user_id: str) -> List[Project]:
    """获取用户的所有项目"""
    try:
        results = await db_client.select(
            TableNames.PROJECTS,
            filters={ProjectFields.USER_ID: user_id}
        )
        return [Project.from_dict(row) for row in results]
    except Exception as e:
        print(f"❌ 获取用户项目失败: {e}")
        return []


async def update_project(
    project_id: str, 
    title: Optional[str] = None,
    description: Optional[str] = None,
    visibility: Optional[ProjectVisibility] = None,
    default_style_prompt: Optional[str] = None
) -> bool:
    """更新项目信息"""
    try:
        updates = {}
        
        if title is not None:
            updates[ProjectFields.TITLE] = title
        if description is not None:
            updates[ProjectFields.DESCRIPTION] = description
        if visibility is not None:
            updates[ProjectFields.VISIBILITY] = visibility.value
        if default_style_prompt is not None:
            updates[ProjectFields.DEFAULT_STYLE_PROMPT] = default_style_prompt
        
        if not updates:
            return True
        
        await db_client.update(
            TableNames.PROJECTS,
            updates,
            {ProjectFields.PROJECT_ID: project_id}
        )
        return True
    except Exception as e:
        print(f"❌ 更新项目失败: {e}")
        return False


async def delete_project(project_id: str) -> bool:
    """删除项目（级联删除相关数据）"""
    try:
        await db_client.delete(
            TableNames.PROJECTS,
            {ProjectFields.PROJECT_ID: project_id}
        )
        return True
    except Exception as e:
        print(f"❌ 删除项目失败: {e}")
        return False


# ==================== 原文相关操作 ====================

async def create_source_text(
    project_id: str,
    title: str,
    raw_content: str,
    order_index: int = 0,
    chapter_number: Optional[int] = None,
    chapter_name: Optional[str] = None
) -> Optional[SourceText]:
    """
    创建原文记录
    
    Args:
        project_id: 项目ID
        title: 标题
        raw_content: 原始内容
        order_index: 排序索引
        chapter_number: 章节编号
        chapter_name: 章节名称
        
    Returns:
        Optional[SourceText]: 创建的原文对象或None
    """
    try:
        text_data = {
            SourceTextFields.TEXT_ID: str(uuid.uuid4()),
            SourceTextFields.PROJECT_ID: project_id,
            SourceTextFields.TITLE: title,
            SourceTextFields.RAW_CONTENT: raw_content,
            SourceTextFields.ORDER_INDEX: order_index,
            SourceTextFields.CHAPTER_NUMBER: chapter_number,
            SourceTextFields.CHAPTER_NAME: chapter_name
        }
        
        result = await db_client.insert(TableNames.SOURCE_TEXTS, text_data)
        if result:
            return SourceText.from_dict(result)
        return None
        
    except Exception as e:
        print(f"❌ 创建原文失败: {e}")
        return None


async def get_source_texts_by_project(project_id: str) -> List[SourceText]:
    """获取项目的所有原文"""
    try:
        results = await db_client.select(
            TableNames.SOURCE_TEXTS,
            filters={SourceTextFields.PROJECT_ID: project_id}
        )
        return [SourceText.from_dict(row) for row in results]
    except Exception as e:
        print(f"❌ 获取项目原文失败: {e}")
        return []


# ==================== 分镜相关操作 ====================

async def create_storyboard_panel(
    project_id: str, 
    source_text_id: str, 
    panel_index: int, 
    panel_data: dict, 
    character_id: Optional[str] = None
) -> Optional[StoryboardPanel]:
    """
    创建一条新的分镜面板记录
    
    Args:
        project_id: 项目ID
        source_text_id: 原文ID
        panel_index: 面板索引
        panel_data: 面板数据字典
        character_id: 角色ID（可选）
        
    Returns:
        Optional[StoryboardPanel]: 创建的分镜面板对象或None
    """
    try:
        storyboard_data = {
            StoryboardFields.STORYBOARD_ID: str(uuid.uuid4()),
            StoryboardFields.PROJECT_ID: project_id,
            StoryboardFields.SOURCE_TEXT_ID: source_text_id,
            StoryboardFields.PANEL_INDEX: panel_index,
            StoryboardFields.ORIGINAL_TEXT_SNIPPET: panel_data.get("original_text_snippet"),
            StoryboardFields.CHARACTER_APPEARANCE: panel_data.get("character_appearance"),
            StoryboardFields.SCENE_AND_LIGHTING: panel_data.get("scene_and_lighting"),
            StoryboardFields.CAMERA_AND_COMPOSITION: panel_data.get("camera_and_composition"),
            StoryboardFields.EXPRESSION_AND_ACTION: panel_data.get("expression_and_action"),
            StoryboardFields.STYLE_REQUIREMENTS: panel_data.get("style_requirements"),
            StoryboardFields.CHARACTER_ID: character_id
        }
        result = await db_client.insert(TableNames.STORYBOARDS, storyboard_data)
        if result:
            return StoryboardPanel.from_dict(result)
        return None
    except Exception as e:
        print(f"❌ 创建分镜面板失败: {e}")
        return None


async def get_storyboards_by_text_id(text_id: str) -> List[StoryboardPanel]:
    """
    根据 source_text_id 获取所有分镜面板，按索引排序
    
    Args:
        text_id: 原文ID
        
    Returns:
        List[StoryboardPanel]: 分镜面板列表
    """
    try:
        results = await db_client.select(
            TableNames.STORYBOARDS,
            filters={StoryboardFields.SOURCE_TEXT_ID: text_id}
        )
        # 在Python中排序
        results.sort(key=lambda x: x.get(StoryboardFields.PANEL_INDEX, 0))
        return [StoryboardPanel.from_dict(row) for row in results]
    except Exception as e:
        print(f"❌ 获取分镜列表失败: {e}")
        return []


async def update_storyboard_panel(storyboard_id: str, updates: dict) -> bool:
    """
    更新单个分镜面板
    
    Args:
        storyboard_id: 分镜面板ID
        updates: 要更新的字段字典
        
    Returns:
        bool: 更新是否成功
    """
    try:
        # 清理掉主键，防止更新主键
        if StoryboardFields.STORYBOARD_ID in updates:
            del updates[StoryboardFields.STORYBOARD_ID]
        
        await db_client.update(
            TableNames.STORYBOARDS,
            updates,
            {StoryboardFields.STORYBOARD_ID: storyboard_id}
        )
        return True
    except Exception as e:
        print(f"❌ 更新分镜面板失败: {e}")
        return False


async def get_storyboard_by_id(storyboard_id: str) -> Optional[StoryboardPanel]:
    """
    根据ID获取分镜面板
    
    Args:
        storyboard_id: 分镜面板ID
        
    Returns:
        Optional[StoryboardPanel]: 分镜面板对象或None
    """
    try:
        results = await db_client.select(
            TableNames.STORYBOARDS,
            filters={StoryboardFields.STORYBOARD_ID: storyboard_id}
        )
        if results:
            return StoryboardPanel.from_dict(results[0])
        return None
    except Exception as e:
        print(f"❌ 获取分镜面板失败: {e}")
        return None


async def delete_storyboard_panel(storyboard_id: str) -> bool:
    """
    删除分镜面板
    
    Args:
        storyboard_id: 分镜面板ID
        
    Returns:
        bool: 删除是否成功
    """
    try:
        await db_client.delete(
            TableNames.STORYBOARDS,
            {StoryboardFields.STORYBOARD_ID: storyboard_id}
        )
        return True
    except Exception as e:
        print(f"❌ 删除分镜面板失败: {e}")
        return False


# ==================== 角色相关操作 ====================

async def create_character(
    project_id: str,
    name: str,
    description: Optional[str] = None,
    reference_image_urls: Optional[List[str]] = None,
    lora_model_path: Optional[str] = None,
    trigger_word: Optional[str] = None
) -> Optional[Character]:
    """
    创建角色
    
    Args:
        project_id: 项目ID
        name: 角色名称
        description: 角色描述
        reference_image_urls: 参考图片URL列表
        lora_model_path: LoRA模型路径
        trigger_word: 触发词
        
    Returns:
        Optional[Character]: 创建的角色对象或None
    """
    try:
        character_data = {
            CharacterFields.CHARACTER_ID: str(uuid.uuid4()),
            CharacterFields.PROJECT_ID: project_id,
            CharacterFields.NAME: name,
            CharacterFields.DESCRIPTION: description,
            CharacterFields.REFERENCE_IMAGE_URLS: reference_image_urls or [],
            CharacterFields.LORA_MODEL_PATH: lora_model_path,
            CharacterFields.TRIGGER_WORD: trigger_word
        }
        
        result = await db_client.insert(TableNames.CHARACTERS, character_data)
        if result:
            return Character.from_dict(result)
        return None
        
    except Exception as e:
        print(f"❌ 创建角色失败: {e}")
        return None


async def get_characters_by_project(project_id: str) -> List[Character]:
    """获取项目的所有角色"""
    try:
        results = await db_client.select(
            TableNames.CHARACTERS,
            filters={CharacterFields.PROJECT_ID: project_id}
        )
        return [Character.from_dict(row) for row in results]
    except Exception as e:
        print(f"❌ 获取项目角色失败: {e}")
        return []


async def update_character(
    character_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    reference_image_urls: Optional[List[str]] = None,
    lora_model_path: Optional[str] = None,
    trigger_word: Optional[str] = None
) -> bool:
    """更新角色信息"""
    try:
        updates = {}
        
        if name is not None:
            updates[CharacterFields.NAME] = name
        if description is not None:
            updates[CharacterFields.DESCRIPTION] = description
        if reference_image_urls is not None:
            updates[CharacterFields.REFERENCE_IMAGE_URLS] = reference_image_urls
        if lora_model_path is not None:
            updates[CharacterFields.LORA_MODEL_PATH] = lora_model_path
        if trigger_word is not None:
            updates[CharacterFields.TRIGGER_WORD] = trigger_word
        
        if not updates:
            return True
        
        await db_client.update(
            TableNames.CHARACTERS,
            updates,
            {CharacterFields.CHARACTER_ID: character_id}
        )
        return True
    except Exception as e:
        print(f"❌ 更新角色失败: {e}")
        return False


async def delete_character(character_id: str) -> bool:
    """删除角色"""
    try:
        await db_client.delete(
            TableNames.CHARACTERS,
            {CharacterFields.CHARACTER_ID: character_id}
        )
        return True
    except Exception as e:
        print(f"❌ 删除角色失败: {e}")
        return False


# ==================== 公共查询操作 ====================

async def get_public_projects(limit: int = 20, offset: int = 0) -> List[Project]:
    """获取公开项目列表"""
    try:
        # Supabase的limit和offset需要特殊处理
        results = await db_client.select(
            TableNames.PROJECTS,
            filters={ProjectFields.VISIBILITY: ProjectVisibility.PUBLIC.value}
        )
        
        # 手动实现limit和offset
        return [Project.from_dict(row) for row in results[offset:offset+limit]]
    except Exception as e:
        print(f"❌ 获取公开项目失败: {e}")
        return []


async def search_projects(keyword: str, limit: int = 20) -> List[Project]:
    """搜索项目"""
    try:
        # Supabase的文本搜索需要特殊处理
        results = await db_client.select(TableNames.PROJECTS)
        
        # 手动过滤包含关键词的项目
        filtered_results = []
        for row in results:
            if (keyword.lower() in row.get(ProjectFields.TITLE, "").lower() or 
                keyword.lower() in row.get(ProjectFields.DESCRIPTION, "").lower()):
                if row.get(ProjectFields.VISIBILITY) == ProjectVisibility.PUBLIC.value:
                    filtered_results.append(row)
        
        return [Project.from_dict(row) for row in filtered_results[:limit]]
    except Exception as e:
        print(f"❌ 搜索项目失败: {e}")
        return []


async def get_user_stats(user_id: str) -> Dict[str, Any]:
    """获取用户统计信息"""
    try:
        # 项目数量
        projects = await get_projects_by_user(user_id)
        project_count = len(projects)
        
        # 原文数量
        text_count = 0
        for project in projects:
            texts = await get_source_texts_by_project(project.project_id)
            text_count += len(texts)
        
        # 角色数量
        character_count = 0
        for project in projects:
            characters = await get_characters_by_project(project.project_id)
            character_count += len(characters)
        
        return {
            "project_count": project_count,
            "text_count": text_count,
            "character_count": character_count
        }
        
    except Exception as e:
        print(f"❌ 获取用户统计失败: {e}")
        return {"project_count": 0, "text_count": 0, "character_count": 0}


# ==================== 状态管理相关操作 ====================

async def update_source_text_status(text_id: str, status: str, error_message: Optional[str] = None):
    """更新 source_texts 表的处理状态和错误信息"""
    try:
        updates = {"processing_status": status}
        if error_message:
            updates["error_message"] = error_message
        await db_client.update(
            TableNames.SOURCE_TEXTS,
            updates,
            {SourceTextFields.TEXT_ID: text_id}
        )
        print(f"   (DB) 更新 text_id {text_id} 状态为: {status}")
    except Exception as e:
        print(f"❌ 更新状态失败 text_id {text_id}: {e}")


async def update_source_text(
    text_id: str,
    title: Optional[str] = None,
    chapter_number: Optional[int] = None,
    chapter_name: Optional[str] = None,
    order_index: Optional[int] = None
) -> bool:
    """更新原文信息"""
    try:
        updates = {}
        
        if title is not None:
            updates[SourceTextFields.TITLE] = title
        if chapter_number is not None:
            updates[SourceTextFields.CHAPTER_NUMBER] = chapter_number
        if chapter_name is not None:
            updates[SourceTextFields.CHAPTER_NAME] = chapter_name
        if order_index is not None:
            updates[SourceTextFields.ORDER_INDEX] = order_index
        
        if not updates:
            return False
        
        await db_client.update(
            TableNames.SOURCE_TEXTS,
            updates,
            {SourceTextFields.TEXT_ID: text_id}
        )
        print(f"✅ 更新原文成功: {text_id}")
        return True
    except Exception as e:
        print(f"❌ 更新原文失败: {e}")
        return False


async def get_source_text_by_id(text_id: str) -> Optional[SourceText]:
    """根据ID获取原文"""
    try:
        results = await db_client.select(
            TableNames.SOURCE_TEXTS,
            filters={SourceTextFields.TEXT_ID: text_id}
        )
        if results:
            # 手动添加 status 和 error 字段到模型（如果模型定义没更新）
            data = results[0]
            st = SourceText.from_dict(data)
            st.processing_status = data.get("processing_status", "pending")
            st.error_message = data.get("error_message")
            return st
        return None
    except Exception as e:
        print(f"❌ 获取原文失败: {e}")
        return None


async def delete_storyboard_panel(storyboard_id: str) -> bool:
    """删除单个分镜面板"""
    try:
        await db_client.delete(
            TableNames.STORYBOARDS,
            {StoryboardFields.STORYBOARD_ID: storyboard_id}
        )
        print(f"✅ 分镜面板删除成功: {storyboard_id}")
        return True
    except Exception as e:
        print(f"❌ 删除分镜面板失败: {e}")
        return False