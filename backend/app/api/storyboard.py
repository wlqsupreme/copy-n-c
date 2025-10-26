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

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入数据库层和服务层
from app.db import (
    db_client, create_source_text, create_character, create_storyboard_panel,
    get_characters_by_project, get_storyboards_by_text_id, update_storyboard_panel,
    update_source_text_status, get_source_text_by_id, delete_storyboard_panel
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
    chapter_number: int | None = None # 章节编号
    chapter_name: str | None = None   # 章节名称


# ==================== 后台处理函数 ====================

async def process_text_background(
    project_id: str,
    text_id: str,
    text_content: str,
    title: Optional[str]
):
    """后台执行 AI 解析和数据库保存"""
    print(f"🔄(Background) 开始处理 text_id: {text_id}")
    try:
        # 标记状态为 processing
        await update_source_text_status(text_id, 'processing')

        # --- 这里是原来 parse_text 中的核心 AI 处理逻辑 ---
        # 1. 获取已存在角色
        existing_db_chars = await get_characters_by_project(project_id)
        existing_char_list_for_ai = [{"name": c.name, "description": c.description} for c in existing_db_chars]
        name_to_id_map = {c.name: c.character_id for c in existing_db_chars}
        print(f"   (BG) 找到 {len(existing_db_chars)} 个已存在角色")

        # 2. 处理分段或单段
        all_new_characters_from_ai = []
        all_storyboards_from_ai = []
        
        # 决定是否需要分段 (可以在这里加一个简单的字数判断)
        needs_segmentation = len(text_content) > 1500 # 举例：超过1500字则分段

        if needs_segmentation:
            print(f"   (BG) 长文本，开始分段处理...")
            segments = await ai_parser.segment_text(text_content, existing_char_list_for_ai)
            print(f"   (BG) 分段完成，共 {len(segments)} 段")

            for i, segment in enumerate(segments):
                print(f"   (BG) 处理第 {i+1}/{len(segments)} 段...")
                ai_response_segment = await ai_parser.generate_storyboard_for_segment(
                    segment["content"], title, i + 1, existing_char_list_for_ai
                )
                all_new_characters_from_ai.extend(ai_response_segment.get("characters", []))
                all_storyboards_from_ai.extend(ai_response_segment.get("storyboards", []))
                print(f"   (BG) 第 {i+1} 段完成")
        else:
            print(f"   (BG) 短文本，直接处理...")
            ai_response_single = await ai_parser.generate_storyboard_for_segment(
                text_content, title, 1, existing_char_list_for_ai
            )
            all_new_characters_from_ai = ai_response_single.get("characters", [])
            all_storyboards_from_ai = ai_response_single.get("storyboards", [])

        print(f"   (BG) AI 处理完成，共识别 {len(all_new_characters_from_ai)} 个新角色，生成 {len(all_storyboards_from_ai)} 个分镜面板")

        # 3. 保存新角色
        if all_new_characters_from_ai:
            print(f"   (BG) 保存新角色...")
            for char_data in all_new_characters_from_ai:
                char_name = char_data.get("name")
                if char_name and char_name not in name_to_id_map:
                    new_char = await create_character(project_id, char_name, char_data.get("description"))
                    if new_char:
                        name_to_id_map[new_char.name] = new_char.character_id
        
        # 4. 保存分镜面板
        if all_storyboards_from_ai:
            print(f"   (BG) 保存分镜面板...")
            for i, panel_data in enumerate(all_storyboards_from_ai):
                await create_storyboard_panel(project_id, text_id, i, panel_data, name_to_id_map)
        # --- AI 处理逻辑结束 ---

        # 标记状态为 completed
        await update_source_text_status(text_id, 'completed')
        print(f"✅(Background) 处理完成 text_id: {text_id}")

    except Exception as e:
        print(f"❌(Background) 处理失败 text_id: {text_id}: {e}")
        import traceback
        error_msg = traceback.format_exc()
        # 标记状态为 failed 并记录错误
        await update_source_text_status(text_id, 'failed', error_msg)

# ==================== API接口定义 ====================

@router.post("/api/v1/parse", tags=["Storyboard"])
async def parse_text(req: ParseRequest, background_tasks: BackgroundTasks):
    """
    解析小说文本并生成分镜（后台任务版本）
    
    功能说明：
    - 接收前端发送的小说文本
    - 先保存原文到source_texts表（状态为pending）
    - 启动后台任务进行AI处理
    - 立即返回text_id供前端轮询状态
    
    使用场景：
    - 用户上传小说文本，系统后台生成分镜
    - 支持长文本自动分段处理
    - 异步处理，不阻塞前端
    
    参数：
        req: ParseRequest - 包含文本内容和配置选项
        background_tasks: BackgroundTasks - FastAPI后台任务
    
    返回：
        dict: 包含成功状态和text_id的JSON响应
    """
    print(f"📖(API) 收到解析请求 (将后台处理):")
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
        # 1. 保存原文 (状态默认为 pending)
        print(f"   (API) 保存原文...")
        source_text = await create_source_text(
            project_id=req.project_id,
            title=req.chapter_name or req.title or "Untitled Chapter",
            raw_content=req.text,
            chapter_number=req.chapter_number,
            chapter_name=req.chapter_name
        )
        if not source_text:
            raise HTTPException(status_code=500, detail="保存原文失败")
        text_id = source_text.text_id
        print(f"   (API) 原文保存成功, text_id: {text_id}, 状态: pending")

        # 2. [关键] 将耗时任务添加到后台
        print(f"   (API) 添加到后台任务队列...")
        background_tasks.add_task(
            process_text_background,
            req.project_id,
            text_id,
            req.text,
            req.title
        )

        # 3. [关键] 立即返回响应给前端
        print(f"   (API) 立即返回响应...")
        return {
            "ok": True,
            "message": "已接收处理请求，正在后台生成...",
            "project_id": req.project_id,
            "text_id": text_id
        }

    except Exception as e:
        print(f"❌(API) 接收解析请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"请求处理失败: {str(e)}")


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


class StoryboardPanelCreate(BaseModel):
    """分镜面板创建请求模型"""
    project_id: str
    source_text_id: str
    panel_index: int
    original_text_snippet: Optional[str] = None
    character_appearance: Optional[str] = None
    scene_and_lighting: Optional[str] = None
    camera_and_composition: Optional[str] = None
    expression_and_action: Optional[str] = None
    style_requirements: Optional[str] = None
    panel_elements: Optional[List[Dict[str, Any]]] = None


@router.post("/api/v1/storyboard", tags=["Storyboard"])
async def create_storyboard(panel_data: StoryboardPanelCreate):
    """
    创建新的分镜面板
    
    功能说明：
    - 允许用户手动创建新的分镜面板
    - 支持所有分镜字段的输入
    - 自动分配panel_index
    
    参数：
        panel_data: 分镜面板数据
    
    返回：
        dict: 创建结果状态
    """
    print(f"➕(API) 创建分镜面板: project_id={panel_data.project_id}")
    
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        from app.db import create_storyboard_panel
        
        # 创建分镜面板数据
        panel_dict = panel_data.dict(exclude_unset=True)
        
        # 调用数据库创建函数
        new_panel = await create_storyboard_panel(
            project_id=panel_data.project_id,
            source_text_id=panel_data.source_text_id,
            panel_index=panel_data.panel_index,
            panel_data=panel_dict,
            name_to_id_map=None  # 手动创建时不需要角色名称映射
        )
        
        if new_panel:
            print(f"✅ 分镜面板创建成功: {new_panel.storyboard_id}")
            return {
                "ok": True, 
                "message": "创建成功",
                "storyboard_id": new_panel.storyboard_id,
                "panel": new_panel.to_dict()
            }
        else:
            print(f"❌ 分镜面板创建失败")
            raise HTTPException(status_code=500, detail="创建失败")
            
    except Exception as e:
        print(f"❌(API) 创建分镜面板失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


class StoryboardPanelUpdate(BaseModel):
    """分镜面板更新请求模型"""
    original_text_snippet: Optional[str] = None
    character_appearance: Optional[str] = None
    scene_and_lighting: Optional[str] = None
    camera_and_composition: Optional[str] = None
    expression_and_action: Optional[str] = None
    style_requirements: Optional[str] = None
    character_id: Optional[str] = None
    dialogue: Optional[str] = None
    panel_elements: Optional[List[Dict[str, Any]]] = None
    panel_index: Optional[int] = None


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


# ==================== 新增API接口 ====================

@router.get("/api/v1/source_text_status/{text_id}", tags=["Storyboard"])
async def get_source_text_status(text_id: str):
    """获取文本处理状态"""
    print(f"❓(API) 查询状态: {text_id}")
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    try:
        source_text = await get_source_text_by_id(text_id)
        if not source_text:
            raise HTTPException(status_code=404, detail="未找到该文本")
        
        return {
            "ok": True,
            "text_id": text_id,
            "status": source_text.processing_status,
            "error": source_text.error_message if source_text.processing_status == 'failed' else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询状态失败: {str(e)}")


@router.delete("/api/v1/storyboard/{storyboard_id}", tags=["Storyboard"])
async def delete_storyboard(storyboard_id: str):
    """删除单个分镜面板"""
    print(f"🗑️(API) 删除分镜面板: {storyboard_id}")
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    try:
        success = await delete_storyboard_panel(storyboard_id)
        if success:
            return {"ok": True, "message": "删除成功"}
        else:
            # 可能未找到或删除失败
            raise HTTPException(status_code=404, detail="未找到或删除失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
