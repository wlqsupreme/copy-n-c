# backend/app/api/text_to_image.py
#
# 文生图相关的API路由
# 
# 这个文件专门负责：
# 1. 接收前端的文生图请求
# 2. 调用文生图服务层生成图片
# 3. 支持单张、多张、分镜配图等场景
# 4. 返回标准化的JSON响应给前端
#
# 设计原则：
# - 只处理HTTP请求/响应，不包含业务逻辑
# - 通过调用services层完成实际工作
# - 统一的错误处理和状态码返回
# - 为前端提供清晰的数据接口

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入文生图服务层
from app.services import text_to_image

# 创建文生图相关的路由器
router = APIRouter(prefix="/api/v1/text-to-image", tags=["Text to Image"])


# ==================== 数据模型定义 ====================

class ImageGenerationRequest(BaseModel):
    """
    图片生成请求模型
    
    用于接收前端发送的文生图请求
    """
    prompt: str = Field(..., description="图片描述文字，详细的描述可以生成更好的图片")
    size: str = Field(default="1024x1024", description="图片尺寸：256x256, 512x512, 1024x1024, 1792x1024, 1024x1792")
    quality: str = Field(default="standard", description="图片质量：standard(标准), hd(高清)")
    style: str = Field(default="vivid", description="图片风格：vivid(生动), natural(自然)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "一只可爱的橘猫坐在窗台上，阳光洒在它身上，温暖的画面",
                "size": "1024x1024",
                "quality": "standard",
                "style": "vivid"
            }
        }
    }


class MultipleImagesRequest(BaseModel):
    """
    批量图片生成请求模型
    
    用于生成多张图片供选择
    """
    prompt: str = Field(..., description="图片描述文字")
    n: int = Field(default=4, ge=1, le=10, description="生成图片数量，1-10之间")
    size: str = Field(default="1024x1024", description="图片尺寸")
    quality: str = Field(default="standard", description="图片质量")
    style: str = Field(default="vivid", description="图片风格")


class StoryboardImagesRequest(BaseModel):
    """
    分镜配图请求模型
    
    用于为漫画分镜生成配图
    """
    scenes: List[dict] = Field(..., description="场景列表，每项包含index和description")
    size: str = Field(default="1024x1024", description="图片尺寸")
    style: str = Field(default="vivid", description="图片风格")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "scenes": [
                    {"index": 1, "description": "清晨的城市街道，阳光透过高楼"},
                    {"index": 2, "description": "主角走进咖啡店，温暖的氛围"}
                ],
                "size": "1024x1024",
                "style": "vivid"
            }
        }
    }


# ==================== API接口定义 ====================

@router.post("/generate")
async def generate_single_image(req: ImageGenerationRequest):
    """
    生成单张图片接口
    
    功能说明：
    - 根据文字描述生成一张图片
    - 返回图片URL和优化后的提示词
    
    使用场景：
    - 用户输入描述生成配图
    - 快速预览效果
    - 单个场景配图
    
    参数：
        req: ImageGenerationRequest - 包含提示词和生成参数
    
    返回：
        dict: 包含图片URL的JSON响应
    """
    print(f"🎨(API) 收到单张图片生成请求")
    print(f"   提示词: {req.prompt[:100]}...")
    print(f"   尺寸: {req.size}")
    print(f"   质量: {req.quality}")
    print(f"   风格: {req.style}")
    
    # 验证参数
    if req.size not in text_to_image.get_supported_sizes():
        raise HTTPException(
            status_code=400,
            detail=f"不支持的尺寸。支持的尺寸: {', '.join(text_to_image.get_supported_sizes())}"
        )
    
    if req.quality not in text_to_image.get_supported_qualities():
        raise HTTPException(
            status_code=400,
            detail=f"不支持的质量。支持的质量: {', '.join(text_to_image.get_supported_qualities())}"
        )
    
    if req.style not in text_to_image.get_supported_styles():
        raise HTTPException(
            status_code=400,
            detail=f"不支持的风格。支持的风格: {', '.join(text_to_image.get_supported_styles())}"
        )
    
    try:
        # 调用文生图服务
        result = await text_to_image.generate_image(
            prompt=req.prompt,
            size=req.size,
            quality=req.quality,
            style=req.style
        )
        
        if result:
            print(f"✅(API) 图片生成成功")
            return {
                "ok": True,
                "image": result,
                "message": "图片生成成功"
            }
        else:
            print(f"❌(API) 图片生成失败")
            raise HTTPException(status_code=500, detail="图片生成失败，请检查提示词或API配置")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 图片生成异常: {e}")
        raise HTTPException(status_code=500, detail=f"图片生成失败: {str(e)}")


@router.post("/generate-multiple")
async def generate_multiple_images(req: MultipleImagesRequest):
    """
    生成多张图片接口
    
    功能说明：
    - 根据同一个描述生成多张图片
    - 提供多个选择供用户挑选最满意的
    
    使用场景：
    - 需要多个候选方案
    - 对比不同效果
    - 提高满意度
    
    参数：
        req: MultipleImagesRequest - 包含提示词和生成数量
    
    返回：
        dict: 包含多张图片URL的列表
    """
    print(f"🎨(API) 收到多张图片生成请求")
    print(f"   数量: {req.n} 张")
    
    # 验证参数
    if req.n < 1 or req.n > 10:
        raise HTTPException(status_code=400, detail="生成数量必须在1-10之间")
    
    try:
        # 调用批量生成服务
        results = await text_to_image.generate_multiple_images(
            prompt=req.prompt,
            n=req.n,
            size=req.size,
            quality=req.quality,
            style=req.style
        )
        
        if results:
            print(f"✅(API) 成功生成 {len(results)} 张图片")
            return {
                "ok": True,
                "images": results,
                "count": len(results),
                "message": f"成功生成 {len(results)} 张图片"
            }
        else:
            print(f"❌(API) 批量生成失败")
            raise HTTPException(status_code=500, detail="批量生成失败")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 批量生成异常: {e}")
        raise HTTPException(status_code=500, detail=f"批量生成失败: {str(e)}")


@router.post("/storyboard")
async def generate_storyboard_images(req: StoryboardImagesRequest):
    """
    分镜配图生成接口
    
    功能说明：
    - 为多个分镜场景批量生成配图
    - 适用于小说转漫画的场景
    - 每个场景生成一张图片
    
    使用场景：
    - 漫画分镜配图
    - 故事板可视化
    - 连续场景展示
    
    参数：
        req: StoryboardImagesRequest - 包含场景列表和生成参数
    
    返回：
        dict: 包含每个场景的配图URL
    """
    print(f"🎬(API) 收到分镜配图请求")
    print(f"   场景数量: {len(req.scenes)}")
    
    if not req.scenes or len(req.scenes) == 0:
        raise HTTPException(status_code=400, detail="场景列表不能为空")
    
    if len(req.scenes) > 20:
        raise HTTPException(status_code=400, detail="单次最多生成20个场景的配图")
    
    try:
        # 调用分镜配图服务
        results = await text_to_image.generate_storyboard_images(
            scenes=req.scenes,
            size=req.size,
            style=req.style
        )
        
        success_count = sum(1 for r in results if r.get("url"))
        print(f"✅(API) 分镜配图完成，成功: {success_count}/{len(req.scenes)}")
        
        return {
            "ok": True,
            "storyboard": results,
            "total": len(results),
            "success_count": success_count,
            "message": f"分镜配图完成，成功生成 {success_count}/{len(req.scenes)} 张"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 分镜配图异常: {e}")
        raise HTTPException(status_code=500, detail=f"分镜配图失败: {str(e)}")


@router.get("/options")
async def get_generation_options():
    """
    获取生成选项接口
    
    功能说明：
    - 返回支持的尺寸、风格、质量选项
    - 供前端构建选择器
    
    返回：
        dict: 所有可用的生成选项
    """
    return {
        "ok": True,
        "options": {
            "sizes": text_to_image.get_supported_sizes(),
            "styles": text_to_image.get_supported_styles(),
            "qualities": text_to_image.get_supported_qualities()
        },
        "descriptions": {
            "sizes": {
                "256x256": "小尺寸，快速生成",
                "512x512": "中等尺寸",
                "1024x1024": "正方形，默认推荐",
                "1792x1024": "横向宽屏",
                "1024x1792": "竖向"
            },
            "styles": {
                "vivid": "生动、鲜艳、富有想象力",
                "natural": "自然、真实、写实风格"
            },
            "qualities": {
                "standard": "标准质量，较快",
                "hd": "高清质量，较慢但更精细"
            }
        }
    }


@router.get("/health")
async def health_check():
    """
    文生图服务健康检查
    
    返回服务状态和配置信息
    """
    from config import config
    
    return {
        "ok": True,
        "service": "文生图服务",
        "api_configured": config.is_valid(),
        "model": config.model,
        "api_base": "https://openai.qiniu.com/v1",
        "backup_api_base": "https://api.qnaigc.com/v1",
        "message": "服务正常运行"
    }


@router.get("/examples")
async def get_prompt_examples():
    """
    获取提示词示例
    
    功能说明：
    - 提供优质的提示词示例
    - 帮助用户了解如何编写好的提示词
    
    返回：
        dict: 分类的提示词示例
    """
    return {
        "ok": True,
        "examples": {
            "人物": [
                "一位优雅的女性站在樱花树下，和服飘逸，春风拂面，唯美画风",
                "科幻战士穿着未来装甲，手持光剑，在未来城市夜景中，赛博朋克风格",
                "可爱的小女孩抱着泰迪熊，温暖的卧室，柔和的灯光，儿童插画风格"
            ],
            "场景": [
                "古老的图书馆，高高的书架，温暖的灯光，神秘的氛围，油画风格",
                "未来城市天际线，霓虹灯闪烁，飞行汽车穿梭，雨夜，赛博朋克",
                "宁静的海边小屋，日落时分，温暖的色调，浪漫氛围"
            ],
            "动物": [
                "一只威武的老虎在丛林中行走，阳光透过树叶，写实风格",
                "可爱的柴犬坐在草地上，蓝天白云，卡通风格",
                "神秘的黑猫站在月光下的屋顶，星空璀璨，梦幻风格"
            ],
            "抽象": [
                "流动的色彩和光线，抽象艺术，充满活力",
                "几何图形的组合，现代艺术，简约风格",
                "水彩笔触，柔和的色调，印象派风格"
            ],
            "漫画分镜": [
                "漫画风格，男主角走在城市街道，背景虚化，特写镜头",
                "漫画风格，两人在咖啡店对话，温馨氛围，中景镜头",
                "漫画风格，激烈的打斗场面，动感十足，广角镜头"
            ]
        },
        "tips": [
            "提示词越详细，生成的图片越符合预期",
            "可以指定风格，如：油画风格、水彩风格、漫画风格等",
            "描述光线、氛围、色调可以让画面更有感觉",
            "指定镜头类型（特写、中景、远景）可以控制构图",
            "使用'高质量'、'精细'、'细节丰富'等词可以提升画质"
        ]
    }

