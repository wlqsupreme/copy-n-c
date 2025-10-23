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

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入数据库层和服务层
from app.db import db_client, save_storyboard, Storyboard
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


class SaveStoryboardRequest(BaseModel):
    """
    分镜保存请求模型
    
    用于接收前端发送的分镜保存请求
    包含项目ID和分镜数据
    """
    project_id: str                   # 项目ID（必需）
    storyboard: Dict[str, Any]        # 分镜数据（JSON格式）


# ==================== API接口定义 ====================

@router.post("/api/v1/parse", tags=["Storyboard"])
async def parse_text(req: ParseRequest):
    """
    解析小说文本并生成分镜
    
    功能说明：
    - 接收前端发送的小说文本
    - 调用AI服务进行智能分段和分镜生成
    - 可选择性地保存到数据库
    - 返回生成的分镜数据给前端
    
    使用场景：
    - 用户上传小说文本，系统生成分镜
    - 支持长文本自动分段处理
    - 支持实时预览和保存功能
    
    参数：
        req: ParseRequest - 包含文本内容和配置选项
    
    返回：
        dict: 包含分镜数据的JSON响应
    """
    print(f"📖(API) 收到解析请求:")
    print(f"   标题: {req.title}")
    print(f"   文本长度: {len(req.text)} 字符")
    print(f"   自动分段: {req.auto_segment}")
    print(f"   项目ID: {req.project_id}")
    
    try:
        # 1. 调用AI服务层处理逻辑
        if req.auto_segment and len(req.text) > 1000:
            print(f"🔄 开始长文本分段处理...")
            # 长文本：先分段，再逐段生成分镜
            segments = await ai_parser.segment_text(req.text)
            print(f"📝 分段完成，共 {len(segments)} 段")
            
            all_pages = []
            for i, segment in enumerate(segments):
                print(f"🎬 处理第 {i+1} 段...")
                pages = await ai_parser.generate_storyboard_for_segment(
                    segment["content"], req.title, i + 1
                )
                all_pages.extend(pages)
                print(f"✅ 第 {i+1} 段完成，生成 {len(pages)} 页")
            
            print(f"🎉 所有分段处理完成，共生成 {len(all_pages)} 页")
            
        else:
            print(f"🎬 直接处理短文本...")
            # 短文本：直接生成分镜
            all_pages = await ai_parser.generate_storyboard_for_segment(
                req.text, req.title, 1
            )
            print(f"✅ 短文本处理完成，生成 {len(all_pages)} 页")
        
        # 2. 创建分镜对象
        storyboard_obj = Storyboard.from_dict({"pages": all_pages})
        
        # 3. 如果提供了项目ID，保存到数据库
        if req.project_id and db_client.is_connected:
            try:
                success = await save_storyboard(req.project_id, storyboard_obj)
                if success:
                    print(f"✅(API) 分镜已保存到项目 {req.project_id}")
                else:
                    print(f"⚠️(API) 分镜保存失败")
            except Exception as e:
                print(f"❌(API) 保存分镜到数据库失败: {e}")
        
        # 4. 返回结果给前端
        return {
            "ok": True, 
            "storyboard": storyboard_obj.to_dict(),
            "segments_count": len(segments) if req.auto_segment and len(req.text) > 1000 else 1
        }
        
    except Exception as e:
        print(f"❌(API) 解析文本失败: {e}")
        raise HTTPException(status_code=500, detail=f"解析文本失败: {str(e)}")


@router.post("/api/v1/save-storyboard", tags=["Storyboard"])
async def save_storyboard_endpoint(req: SaveStoryboardRequest):
    """
    保存分镜数据到数据库
    
    功能说明：
    - 接收前端发送的分镜数据
    - 验证数据格式和项目ID
    - 保存到Supabase数据库
    - 返回保存结果状态
    
    使用场景：
    - 用户编辑分镜后手动保存
    - 定时自动保存功能
    - 分镜数据的持久化存储
    
    参数：
        req: SaveStoryboardRequest - 包含项目ID和分镜数据
    
    返回：
        dict: 保存结果状态
    """
    print(f"💾(API) 收到保存请求: {req.project_id}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 1. 验证和转换分镜数据
        storyboard = Storyboard.from_dict(req.storyboard)
        
        # 2. 保存到数据库
        success = await save_storyboard(req.project_id, storyboard)
        
        if success:
            print(f"✅(API) 分镜保存成功: {req.project_id}")
            return {"ok": True, "message": "分镜保存成功"}
        else:
            print(f"❌(API) 分镜保存失败: {req.project_id}")
            raise HTTPException(status_code=500, detail="分镜保存失败")
            
    except Exception as e:
        print(f"❌(API) 保存分镜失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存分镜失败: {str(e)}")
