# backend/app/api/storyboard.py
#
# 分镜相关的API路由
# 
# 这个文件专门负责：
# 1. 接收前端Vue页面的分镜相关请求
# 2. 调用AI服务层进行文本解析和分镜生成
# 3. 调用数据库层保存和加载分镜数据
# 4. 返回标准化的JSON响应给前端
#
# 设计原则：
# - 只处理HTTP请求/响应，不包含业务逻辑
# - 通过调用services层和db层完成实际工作
# - 统一的错误处理和状态码返回
# - 为前端提供清晰的数据接口

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, Optional
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入数据库层和服务层
from app.db import (
    db_client, create_source_text, create_character, create_storyboard_panel,
    get_characters_by_project, get_storyboards_by_text_id, update_storyboard_panel
)
from app.services import ai_parser

# 创建分镜相关的路由器
router = APIRouter()

# ==================== 数据模型定义 ====================

class ParseRequest(BaseModel):
    """
    文本解析请求模型
    
    用于接收前端发送的小说文本解析请求
    包含标题、文本内容、分段选项等信息
    """
    title: str | None = None          # 小说标题（可选）
    text: str                         # 要解析的小说文本（必需）
    auto_segment: bool = True         # 是否自动分段（默认开启）
    user_id: str | None = None        # 用户ID（可选，用于权限控制）
    project_id: str | None = None    # 项目ID（可选，用于保存到数据库）


# ==================== API接口定义 ====================

@router.post("/api/v1/parse", tags=["Storyboard"])
async def parse_text(req: ParseRequest):
    """
    解析小说文本并生成分镜
    
    功能说明：
    - 接收前端发送的小说文本
    - 先保存原文到source_texts表
    - 调用AI服务进行智能分段和分镜生成
    - 分别保存角色和分镜到数据库
    - 返回text_id供前端跳转使用
    
    使用场景：
    - 用户上传小说文本，系统生成分镜
    - 支持长文本自动分段处理
    - 数据持久化存储
    
    参数：
        req: ParseRequest - 包含文本内容和配置选项
    
    返回：
        dict: 包含成功状态和text_id的JSON响应
    """
    print(f"📖(API) 收到解析请求:")
    print(f"   标题: {req.title}")
    print(f"   文本长度: {len(req.text)} 字符")
    print(f"   自动分段: {req.auto_segment}")
    print(f"   项目ID: {req.project_id}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    if not req.project_id:
        raise HTTPException(status_code=400, detail="项目ID不能为空")
    
    try:
        # 1. 先保存原文到source_texts表
        print(f"💾 保存原文到数据库...")
        source_text = await create_source_text(
            project_id=req.project_id,
            title=req.title or "Untitled Chapter",
            raw_content=req.text,
            order_index=0
        )
        
        if not source_text:
            raise HTTPException(status_code=500, detail="保存原文失败")
        
        text_id = source_text.text_id
        print(f"✅ 原文保存成功，text_id: {text_id}")
        
        # 2. 获取本项目中已存在的角色
        print(f"👥 查询项目中已存在的角色...")
        existing_db_chars = await get_characters_by_project(req.project_id)
        existing_char_list_for_ai = [
            {"name": c.name, "description": c.description} for c in existing_db_chars
        ]
        print(f"✅ 找到 {len(existing_char_list_for_ai)} 个已存在的角色")
        
        # 3. 调用AI服务层处理逻辑
        if req.auto_segment and len(req.text) > 1000:
            print(f"🔄 开始长文本分段处理...")
            # 长文本：先分段，再逐段生成分镜
            segments = await ai_parser.segment_text(req.text, existing_char_list_for_ai)
            print(f"📝 分段完成，共 {len(segments)} 段")
            
            all_characters = []
            all_storyboards = []
            
            for i, segment in enumerate(segments):
                print(f"🎬 处理第 {i+1} 段...")
                result = await ai_parser.generate_storyboard_for_segment(
                    segment["content"], req.title, i + 1, existing_char_list_for_ai
                )
                
                # 合并角色和分镜数据
                all_characters.extend(result.get("characters", []))
                all_storyboards.extend(result.get("storyboards", []))
                print(f"✅ 第 {i+1} 段完成，新角色: {len(result.get('characters', []))}, 分镜: {len(result.get('storyboards', []))}")
            
            print(f"🎉 所有分段处理完成，新角色: {len(all_characters)}, 总分镜: {len(all_storyboards)}")
            
        else:
            print(f"🎬 直接处理短文本...")
            # 短文本：直接生成分镜
            result = await ai_parser.generate_storyboard_for_segment(
                req.text, req.title, 1, existing_char_list_for_ai
            )
            all_characters = result.get("characters", [])
            all_storyboards = result.get("storyboards", [])
            print(f"✅ 短文本处理完成，新角色: {len(all_characters)}, 分镜: {len(all_storyboards)}")
        
        # 4. 准备名称 -> ID 的映射表，用于后续链接
        name_to_id_map = {c.name: c.character_id for c in existing_db_chars}
        
        # 5. 处理AI返回的"新"角色 (AI不应返回已存在的角色)
        print(f"👥 处理新角色...")
        if all_characters:
            for char_data in all_characters:
                char_name = char_data.get("name")
                # 再次检查，防止AI出错重复返回
                if char_name and char_name not in name_to_id_map:
                    print(f"🧬(API) 发现新角色，正在创建: {char_name}")
                    new_char = await create_character(
                        project_id=req.project_id,
                        name=char_name,
                        description=char_data.get("description")
                    )
                    if new_char:
                        name_to_id_map[new_char.name] = new_char.character_id  # 添加到映射表
                        print(f"✅ 新角色保存成功: {char_name} -> {new_char.character_id}")
                else:
                    print(f"⚠️ 角色已存在，跳过: {char_name}")
        else:
            print(f"ℹ️ 没有新角色需要创建")
        
        # 6. 处理分镜 (这个逻辑基本不变，但现在 name_to_id_map 是完整的)
        print(f"🎬 保存分镜到数据库...")
        for i, panel_data in enumerate(all_storyboards):
            char_name = panel_data.get("character_name")
            char_id = name_to_id_map.get(char_name) if char_name else None
            
            storyboard_panel = await create_storyboard_panel(
                project_id=req.project_id,
                source_text_id=text_id,
                panel_index=i,
                panel_data=panel_data,
                character_id=char_id
            )
            
            if storyboard_panel:
                print(f"✅ 分镜保存成功: panel {i}")
            else:
                print(f"⚠️ 分镜保存失败: panel {i}")
        
        # 7. 返回成功响应
        print(f"🎉 解析完成！text_id: {text_id}")
        return {
            "ok": True,
            "project_id": req.project_id,
            "text_id": text_id,
            "new_characters_count": len(all_characters),
            "storyboards_count": len(all_storyboards)
        }
        
    except Exception as e:
        print(f"❌(API) 解析文本失败: {e}")
        raise HTTPException(status_code=500, detail=f"解析文本失败: {str(e)}")


# ==================== 新增API接口 ====================

@router.get("/api/v1/storyboards", tags=["Storyboard"])
async def get_storyboards(text_id: str = Query(...)):
    """
    根据 text_id 获取分镜面板列表
    
    功能说明：
    - 根据原文ID获取所有相关的分镜面板
    - 按panel_index排序返回
    - 用于前端分镜编辑页面加载数据
    
    参数：
        text_id: 原文ID（必需）
    
    返回：
        dict: 包含分镜面板列表的JSON响应
    """
    print(f"📋(API) 获取分镜列表: text_id={text_id}")
    
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        from app.db import get_storyboards_by_text_id
        panels = await get_storyboards_by_text_id(text_id)
        
        # 转换为字典格式
        panels_data = [panel.to_dict() for panel in panels]
        
        print(f"✅ 获取分镜成功，共 {len(panels_data)} 个面板")
        return {"ok": True, "storyboards": panels_data}
        
    except Exception as e:
        print(f"❌(API) 获取分镜失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分镜失败: {str(e)}")


class StoryboardPanelUpdate(BaseModel):
    """分镜面板更新请求模型"""
    original_text_snippet: Optional[str] = None
    character_appearance: Optional[str] = None
    scene_and_lighting: Optional[str] = None
    camera_and_composition: Optional[str] = None
    expression_and_action: Optional[str] = None
    style_requirements: Optional[str] = None
    character_id: Optional[str] = None


@router.put("/api/v1/storyboard/{storyboard_id}", tags=["Storyboard"])
async def update_storyboard(storyboard_id: str, updates: StoryboardPanelUpdate):
    """
    更新单个分镜面板
    
    功能说明：
    - 允许前端修改单个分镜面板的各个字段
    - 支持部分字段更新
    - 用于分镜编辑功能
    
    参数：
        storyboard_id: 分镜面板ID
        updates: 要更新的字段
    
    返回：
        dict: 更新结果状态
    """
    print(f"✏️(API) 更新分镜面板: {storyboard_id}")
    
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        from app.db import update_storyboard_panel
        
        # .dict(exclude_unset=True) 确保只更新传入的字段
        success = await update_storyboard_panel(storyboard_id, updates.dict(exclude_unset=True))
        
        if success:
            print(f"✅ 分镜面板更新成功: {storyboard_id}")
            return {"ok": True, "message": "更新成功"}
        else:
            print(f"❌ 分镜面板更新失败: {storyboard_id}")
            raise HTTPException(status_code=500, detail="更新失败")
            
    except Exception as e:
        print(f"❌(API) 更新分镜面板失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")
