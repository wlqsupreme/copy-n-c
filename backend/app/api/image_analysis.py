# backend/app/api/image_analysis.py
#
# 图片分析相关的API路由
# 
# 这个文件专门负责：
# 1. 接收前端的图片分析请求（URL或base64）
# 2. 调用图生文服务层进行图片理解
# 3. 支持OCR文字提取
# 4. 支持场景描述生成
# 5. 返回标准化的JSON响应给前端
#
# 设计原则：
# - 只处理HTTP请求/响应，不包含业务逻辑
# - 通过调用services层完成实际工作
# - 统一的错误处理和状态码返回
# - 为前端提供清晰的数据接口

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List
import base64
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入图生文服务层
from app.services import image_to_text

# 创建图片分析相关的路由器
router = APIRouter(prefix="/api/v1/image", tags=["Image Analysis"])


# ==================== 数据模型定义 ====================

class ImageAnalysisRequest(BaseModel):
    """
    图片分析请求模型
    
    用于接收前端发送的图片分析请求
    支持URL和base64两种图片输入方式
    """
    image_url: Optional[str] = None       # 图片URL（与image_base64二选一）
    image_base64: Optional[str] = None    # base64图片数据（与image_url二选一）
    prompt: Optional[str] = None          # 自定义提示词（可选）


class OCRRequest(BaseModel):
    """
    OCR文字提取请求模型
    
    用于从图片中识别和提取文字
    """
    image_url: Optional[str] = None       # 图片URL
    image_base64: Optional[str] = None    # base64图片数据


class SceneDescriptionRequest(BaseModel):
    """
    场景描述生成请求模型
    
    用于生成适合漫画分镜的场景描述
    """
    image_url: Optional[str] = None       # 图片URL
    image_base64: Optional[str] = None    # base64图片数据
    style: str = "detailed"               # 描述风格：detailed/simple/storyboard


class BatchAnalysisRequest(BaseModel):
    """
    批量图片分析请求模型
    
    用于同时分析多张图片
    """
    images: List[dict]                    # 图片列表 [{"url": "..."}, {"base64": "..."}]
    prompt: Optional[str] = None          # 统一的分析提示词


# ==================== API接口定义 ====================

@router.post("/analyze")
async def analyze_image(req: ImageAnalysisRequest):
    """
    图片内容分析接口
    
    功能说明：
    - 接收图片（URL或base64）
    - 使用AI分析图片内容
    - 返回详细的图片描述
    
    使用场景：
    - 用户上传图片了解内容
    - 图片理解和场景识别
    - 为图片生成描述文本
    
    参数：
        req: ImageAnalysisRequest - 包含图片和可选的提示词
    
    返回：
        dict: 包含分析结果的JSON响应
    """
    print(f"🖼️(API) 收到图片分析请求")
    
    # 验证输入
    if not req.image_url and not req.image_base64:
        raise HTTPException(status_code=400, detail="必须提供image_url或image_base64之一")
    
    try:
        # 调用图生文服务
        if req.image_url:
            print(f"🔗 使用URL模式: {req.image_url[:100]}...")
            result = await image_to_text.analyze_image_from_url(req.image_url, req.prompt)
        else:
            print(f"📦 使用base64模式")
            result = await image_to_text.analyze_image_from_base64(req.image_base64, req.prompt)
        
        if result:
            print(f"✅(API) 图片分析成功")
            return {
                "ok": True,
                "result": result,
                "message": "图片分析成功"
            }
        else:
            print(f"❌(API) 图片分析失败")
            raise HTTPException(status_code=500, detail="图片分析失败，请检查图片格式或API配置")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 图片分析异常: {e}")
        raise HTTPException(status_code=500, detail=f"图片分析失败: {str(e)}")


@router.post("/ocr")
async def extract_text(req: OCRRequest):
    """
    OCR文字提取接口
    
    功能说明：
    - 从图片中识别和提取文字
    - 支持多种语言
    - 保持文字的原有布局
    
    使用场景：
    - 扫描文档识别
    - 图片文字提取
    - 书籍、海报等文字识别
    
    参数：
        req: OCRRequest - 包含图片数据
    
    返回：
        dict: 包含提取的文字内容
    """
    print(f"📝(API) 收到OCR文字提取请求")
    
    # 验证输入
    if not req.image_url and not req.image_base64:
        raise HTTPException(status_code=400, detail="必须提供image_url或image_base64之一")
    
    try:
        # 调用OCR服务
        result = await image_to_text.extract_text_from_image(
            image_url=req.image_url,
            image_base64=req.image_base64
        )
        
        if result:
            print(f"✅(API) OCR提取成功")
            return {
                "ok": True,
                "text": result,
                "message": "文字提取成功"
            }
        else:
            print(f"❌(API) OCR提取失败")
            raise HTTPException(status_code=500, detail="文字提取失败，请检查图片清晰度或API配置")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) OCR提取异常: {e}")
        raise HTTPException(status_code=500, detail=f"文字提取失败: {str(e)}")


@router.post("/scene-description")
async def generate_scene_desc(req: SceneDescriptionRequest):
    """
    场景描述生成接口
    
    功能说明：
    - 生成适合漫画分镜的场景描述
    - 包含构图、氛围、人物动作等要素
    - 支持多种描述风格
    
    使用场景：
    - 漫画分镜参考
    - 场景设计灵感
    - 图片转分镜脚本
    
    参数：
        req: SceneDescriptionRequest - 包含图片和风格选项
    
    返回：
        dict: 包含场景描述文本
    """
    print(f"🎬(API) 收到场景描述生成请求，风格: {req.style}")
    
    # 验证输入
    if not req.image_url and not req.image_base64:
        raise HTTPException(status_code=400, detail="必须提供image_url或image_base64之一")
    
    # 验证风格参数
    valid_styles = ["detailed", "simple", "storyboard"]
    if req.style not in valid_styles:
        raise HTTPException(
            status_code=400, 
            detail=f"无效的风格参数，必须是: {', '.join(valid_styles)}"
        )
    
    try:
        # 调用场景描述服务
        result = await image_to_text.generate_scene_description(
            image_url=req.image_url,
            image_base64=req.image_base64,
            style=req.style
        )
        
        if result:
            print(f"✅(API) 场景描述生成成功")
            return {
                "ok": True,
                "description": result,
                "style": req.style,
                "message": "场景描述生成成功"
            }
        else:
            print(f"❌(API) 场景描述生成失败")
            raise HTTPException(status_code=500, detail="场景描述生成失败")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 场景描述生成异常: {e}")
        raise HTTPException(status_code=500, detail=f"场景描述生成失败: {str(e)}")


@router.post("/batch-analyze")
async def batch_analyze(req: BatchAnalysisRequest):
    """
    批量图片分析接口
    
    功能说明：
    - 同时分析多张图片
    - 每张图片独立分析
    - 返回对应的分析结果列表
    
    使用场景：
    - 连续分镜图片分析
    - 图片集批量处理
    - 多图对比分析
    
    参数：
        req: BatchAnalysisRequest - 包含图片列表和提示词
    
    返回：
        dict: 包含批量分析结果
    """
    print(f"📚(API) 收到批量分析请求，共 {len(req.images)} 张图片")
    
    if not req.images or len(req.images) == 0:
        raise HTTPException(status_code=400, detail="图片列表不能为空")
    
    if len(req.images) > 20:
        raise HTTPException(status_code=400, detail="单次最多分析20张图片")
    
    try:
        # 调用批量分析服务
        results = await image_to_text.batch_analyze_images(req.images, req.prompt)
        
        success_count = sum(1 for r in results if r["success"])
        print(f"✅(API) 批量分析完成，成功: {success_count}/{len(req.images)}")
        
        return {
            "ok": True,
            "results": results,
            "total": len(req.images),
            "success_count": success_count,
            "message": f"批量分析完成，成功处理 {success_count}/{len(req.images)} 张图片"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 批量分析异常: {e}")
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    图片上传接口
    
    功能说明：
    - 接收前端上传的图片文件
    - 自动转换为base64编码
    - 直接返回图片分析结果
    
    使用场景：
    - 前端文件上传
    - 本地图片分析
    - 一键上传并分析
    
    参数：
        file: UploadFile - 上传的图片文件
    
    返回：
        dict: 包含base64编码和分析结果
    """
    print(f"📤(API) 收到图片上传: {file.filename}")
    
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    
    # 验证文件大小（限制10MB）
    file_size = 0
    try:
        # 读取文件内容
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="图片大小不能超过10MB")
        
        print(f"📦 文件大小: {file_size / 1024:.2f} KB")
        
        # 转换为base64
        base64_data = base64.b64encode(contents).decode('utf-8')
        print(f"✅ 转换为base64成功")
        
        # 自动分析图片
        result = await image_to_text.analyze_image_from_base64(base64_data)
        
        if result:
            print(f"✅(API) 图片上传并分析成功")
            return {
                "ok": True,
                "filename": file.filename,
                "size": file_size,
                "base64": f"data:{file.content_type};base64,{base64_data}",
                "analysis": result,
                "message": "图片上传并分析成功"
            }
        else:
            # 即使分析失败，也返回base64数据
            print(f"⚠️(API) 图片上传成功，但分析失败")
            return {
                "ok": True,
                "filename": file.filename,
                "size": file_size,
                "base64": f"data:{file.content_type};base64,{base64_data}",
                "analysis": None,
                "message": "图片上传成功，但分析失败"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 图片上传异常: {e}")
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    图片分析服务健康检查
    
    返回服务状态和配置信息
    """
    from config import config
    
    return {
        "ok": True,
        "service": "图片分析服务",
        "api_configured": config.is_valid(),
        "model": config.model,
        "message": "服务正常运行"
    }

