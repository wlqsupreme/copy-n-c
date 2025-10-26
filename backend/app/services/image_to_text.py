# backend/app/services/image_to_text.py
#
# 图生文服务层 - 图片理解和文字提取的核心逻辑
# 
# 这个文件专门负责：
# 1. 调用七牛云AI API进行图片理解
# 2. 图片OCR文字提取
# 3. 图片场景描述生成
# 4. 支持base64和URL两种图片输入方式
#
# 设计原则：
# - 纯业务逻辑，不涉及HTTP请求/响应
# - 可独立测试和复用
# - 统一的错误处理

import httpx
import json
import os
import sys
import base64
from typing import Optional, Dict, Any

# 添加 backend 目录到 Python 路径，确保能导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config

# 七牛云OpenAI兼容API入口
QINIU_API_BASE = "https://openai.qiniu.com/v1"


async def call_qiniu_vision_api(messages: list) -> Optional[str]:
    """
    调用七牛云视觉理解API
    
    功能说明：
    - 支持图片理解、OCR、场景描述等多模态AI能力
    - 自动处理认证、超时、错误重试等
    - 支持图片URL和base64两种输入方式
    
    参数：
        messages: OpenAI格式的消息列表，包含图片和提示词
    
    返回：
        str: AI生成的文本内容，失败时返回None
    """
    # 构建API请求参数
    payload = {
        "model": config.model,           # AI模型名称
        "messages": messages,            # 对话消息（包含图片）
        "max_tokens": config.max_tokens, # 最大生成token数
        "temperature": config.temperature # 创造性程度
    }

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }

    url = f"{QINIU_API_BASE}/chat/completions"
    
    print(f"🖼️(图生文服务) 开始调用七牛云视觉API...")
    print(f"📡 URL: {url}")
    print(f"🤖 模型: {config.model}")

    # 发送HTTP请求
    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            print(f"📤 发送图片分析请求...")
            r = await client.post(url, headers=headers, json=payload)
            print(f"📥 收到响应: {r.status_code}")
            
            # 检查HTTP状态码
            if r.status_code != 200:
                print(f"❌ API响应错误: {r.status_code}")
                print(f"📄 响应内容: {r.text}")
                try:
                    error_data = r.json()
                    print(f"🔍 错误详情: {error_data}")
                except:
                    print(f"🔍 无法解析错误响应为JSON")
                return None
            
            print(f"✅ API调用成功!")
            data = r.json()
            
        except httpx.RequestError as e:
            print(f"❌(图生文服务) 网络请求失败: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            return None
        except Exception as e:
            print(f"❌(图生文服务) API调用失败: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            return None

    # 提取AI返回的文本内容
    try:
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if content:
            print(f"✅(图生文服务) 成功提取文本，长度: {len(content)} 字符")
            return content
        else:
            print(f"❌(图生文服务) 响应中没有找到content字段")
            return None
    except Exception as e:
        print(f"❌(图生文服务) 解析响应失败: {e}")
        return None


async def analyze_image_from_url(image_url: str, prompt: Optional[str] = None) -> Optional[str]:
    """
    从图片URL分析图片内容
    
    功能说明：
    - 支持通过URL访问的图片
    - 可自定义分析提示词
    - 适用于在线图片、公开链接等场景
    
    参数：
        image_url: 图片的URL地址
        prompt: 自定义提示词，如不提供则使用默认提示词
    
    返回：
        str: 图片分析结果文本
    """
    print(f"🔗(图生文服务) 分析URL图片: {image_url[:100]}...")
    
    if prompt is None:
        prompt = "请详细描述这张图片的内容，包括场景、人物、物品、氛围等细节。"
    
    # 构建OpenAI视觉API格式的消息
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }
    ]
    
    result = await call_qiniu_vision_api(messages)
    if result:
        print(f"✅(图生文服务) URL图片分析成功")
    else:
        print(f"❌(图生文服务) URL图片分析失败")
    
    return result


async def analyze_image_from_base64(image_base64: str, prompt: Optional[str] = None) -> Optional[str]:
    """
    从base64编码的图片数据分析图片内容
    
    功能说明：
    - 支持base64编码的图片数据
    - 可自定义分析提示词
    - 适用于前端上传、本地图片等场景
    
    参数：
        image_base64: base64编码的图片数据（可带或不带data:image前缀）
        prompt: 自定义提示词，如不提供则使用默认提示词
    
    返回：
        str: 图片分析结果文本
    """
    print(f"📦(图生文服务) 分析base64图片...")
    
    if prompt is None:
        prompt = "请详细描述这张图片的内容，包括场景、人物、物品、氛围等细节。"
    
    # 确保base64数据格式正确
    if not image_base64.startswith("data:image"):
        # 自动添加data URL前缀
        image_base64 = f"data:image/jpeg;base64,{image_base64}"
    
    # 构建OpenAI视觉API格式的消息
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_base64
                    }
                }
            ]
        }
    ]
    
    result = await call_qiniu_vision_api(messages)
    if result:
        print(f"✅(图生文服务) base64图片分析成功")
    else:
        print(f"❌(图生文服务) base64图片分析失败")
    
    return result


async def extract_text_from_image(image_url: Optional[str] = None, 
                                   image_base64: Optional[str] = None) -> Optional[str]:
    """
    从图片中提取文字（OCR功能）
    
    功能说明：
    - 专门用于从图片中识别和提取文字
    - 支持URL和base64两种输入方式
    - 使用OCR优化的提示词
    
    参数：
        image_url: 图片URL（与image_base64二选一）
        image_base64: base64图片数据（与image_url二选一）
    
    返回：
        str: 提取的文字内容
    """
    print(f"📝(图生文服务) 开始OCR文字提取...")
    
    ocr_prompt = "请识别并提取图片中的所有文字内容，按原有布局和顺序输出。如果图片中没有文字，请说明。"
    
    if image_url:
        return await analyze_image_from_url(image_url, ocr_prompt)
    elif image_base64:
        return await analyze_image_from_base64(image_base64, ocr_prompt)
    else:
        print(f"❌(图生文服务) 必须提供image_url或image_base64之一")
        return None


async def generate_scene_description(image_url: Optional[str] = None,
                                     image_base64: Optional[str] = None,
                                     style: str = "detailed") -> Optional[str]:
    """
    生成图片的场景描述（用于漫画分镜等）
    
    功能说明：
    - 生成适合漫画分镜的场景描述
    - 包含构图、氛围、人物动作等要素
    - 支持多种描述风格
    
    参数：
        image_url: 图片URL（与image_base64二选一）
        image_base64: base64图片数据（与image_url二选一）
        style: 描述风格 - "detailed"(详细), "simple"(简洁), "storyboard"(分镜)
    
    返回：
        str: 场景描述文本
    """
    print(f"🎬(图生文服务) 生成场景描述，风格: {style}...")
    
    # 根据风格选择提示词
    style_prompts = {
        "detailed": "请详细描述这张图片，包括：1)场景环境 2)人物外貌和动作 3)物品和道具 4)氛围和情绪 5)色彩和光影。",
        "simple": "请简洁描述这张图片的主要内容和氛围。",
        "storyboard": "请用漫画分镜的角度描述这张图片，包括：1)镜头类型（远景/中景/近景/特写）2)人物表情和动作 3)场景元素 4)氛围营造。"
    }
    
    scene_prompt = style_prompts.get(style, style_prompts["detailed"])
    
    if image_url:
        return await analyze_image_from_url(image_url, scene_prompt)
    elif image_base64:
        return await analyze_image_from_base64(image_base64, scene_prompt)
    else:
        print(f"❌(图生文服务) 必须提供image_url或image_base64之一")
        return None


async def batch_analyze_images(images: list, prompt: Optional[str] = None) -> list:
    """
    批量分析多张图片
    
    功能说明：
    - 同时分析多张图片
    - 每张图片独立分析，返回列表
    - 适用于连续分镜、图片集等场景
    
    参数：
        images: 图片列表，每项包含 {"url": "..."} 或 {"base64": "..."}
        prompt: 统一的分析提示词
    
    返回：
        list: 分析结果列表，与输入顺序对应
    """
    print(f"📚(图生文服务) 批量分析 {len(images)} 张图片...")
    
    results = []
    for i, image_data in enumerate(images):
        print(f"🖼️ 分析第 {i+1}/{len(images)} 张图片...")
        
        if "url" in image_data:
            result = await analyze_image_from_url(image_data["url"], prompt)
        elif "base64" in image_data:
            result = await analyze_image_from_base64(image_data["base64"], prompt)
        else:
            print(f"⚠️ 第 {i+1} 张图片格式错误，跳过")
            result = None
        
        results.append({
            "index": i + 1,
            "result": result,
            "success": result is not None
        })
    
    success_count = sum(1 for r in results if r["success"])
    print(f"✅(图生文服务) 批量分析完成，成功: {success_count}/{len(images)}")
    
    return results

