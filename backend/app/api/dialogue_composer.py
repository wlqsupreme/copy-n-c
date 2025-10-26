# backend/app/api/dialogue_composer.py
#
# 对话框合成API
# 
# 功能：
# 1. 接收图片（base64）和对话内容
# 2. 在图片上自动添加对话框
# 3. 返回合成后的图片
#
# 这个API独立于数据库，可以直接测试对话框效果

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.services.comic_composer import add_dialogues_to_image

# 创建路由器
router = APIRouter(prefix="/api/v1/dialogue", tags=["Dialogue Composer"])


class DialogueComposerRequest(BaseModel):
    """对话框合成请求模型"""
    image_base64: str                      # 原始图片的base64编码
    dialogues: List[Dict]                  # 对话列表
    camera_angle: Optional[str] = None     # 镜头角度（可选）


@router.post("/compose")
async def compose_dialogue(req: DialogueComposerRequest):
    """
    在图片上添加对话框
    
    请求示例：
    {
        "image_base64": "data:image/png;base64,iVBORw0KG...",
        "dialogues": [
            {
                "text": "你好，很高兴见到你！",
                "speaker": "李慕白",
                "position": "top_left",
                "bubble_type": "speech"
            }
        ],
        "camera_angle": "中景"
    }
    
    返回：
    {
        "ok": true,
        "image": "data:image/png;base64,iVBORw0KG...",
        "message": "对话框添加成功"
    }
    """
    print(f"🎨(API) 收到对话框合成请求")
    print(f"   对话数量: {len(req.dialogues)}")
    
    try:
        # 调用对话框合成服务
        result_image = add_dialogues_to_image(
            image_base64=req.image_base64,
            dialogues=req.dialogues,
            camera_angle=req.camera_angle
        )
        
        print(f"✅(API) 对话框合成成功")
        
        return {
            "ok": True,
            "image": result_image,
            "dialogue_count": len(req.dialogues),
            "message": f"成功添加 {len(req.dialogues)} 个对话框"
        }
        
    except Exception as e:
        print(f"❌(API) 对话框合成失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"对话框合成失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "ok": True,
        "service": "对话框合成服务",
        "message": "服务正常运行"
    }

