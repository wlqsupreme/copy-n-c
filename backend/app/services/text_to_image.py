# backend/app/services/text_to_image.py
#
# 文生图服务层 - 文字生成图片的核心逻辑
# 
# 这个文件专门负责：
# 1. 调用七牛云AI文生图API
# 2. 根据文字描述生成图片
# 3. 支持多种图片尺寸和风格
# 4. 批量生成多张图片
#
# 设计原则：
# - 纯业务逻辑，不涉及HTTP请求/响应
# - 可独立测试和复用
# - 统一的错误处理

import httpx
import json
import os
import sys
from typing import Optional, Dict, Any, List

# 添加 backend 目录到 Python 路径，确保能导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config

# 七牛云OpenAI兼容API入口
QINIU_API_BASE = "https://openai.qiniu.com/v1"
# 备用接入点
QINIU_API_BASE_BACKUP = "https://api.qnaigc.com/v1"


async def call_qiniu_image_gen_api(prompt: str, 
                                    size: str = "1024x1024",
                                    n: int = 1,
                                    quality: str = "standard",
                                    style: str = "vivid",
                                    use_backup: bool = False) -> Optional[Dict[str, Any]]:
    """
    调用七牛云文生图API
    
    功能说明：
    - 根据文字描述生成图片
    - 支持多种尺寸和风格
    - 自动处理认证、超时、错误重试等
    
    参数：
        prompt: 图片描述文字（必需）
        size: 图片尺寸，支持 "256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"
        n: 生成图片数量，1-10之间
        quality: 图片质量，"standard" 或 "hd"
        style: 图片风格，"vivid" (生动) 或 "natural" (自然)
        use_backup: 是否使用备用接入点
    
    返回：
        dict: 包含图片URL列表的响应数据，失败时返回None
    """
    # 选择接入点
    api_base = QINIU_API_BASE_BACKUP if use_backup else QINIU_API_BASE
    
    # 使用七牛云图像生成专用模型
    image_model = "gemini-2.5-flash-image"  # 七牛云文生图专用模型
    
    # 构建API请求参数
    payload = {
        "model": image_model,  # 使用图像生成模型
        "prompt": prompt,
        "n": n,
        "size": size,
        "quality": quality,
        "style": style
    }

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }

    url = f"{api_base}/images/generations"
    
    print(f"🎨(文生图服务) 开始调用七牛云文生图API...")
    print(f"📡 接入点: {api_base}")
    print(f"🤖 模型: {image_model}")
    print(f"📝 提示词: {prompt[:100]}...")
    print(f"📐 尺寸: {size}")
    print(f"🔢 数量: {n}")
    print(f"✨ 风格: {style}")

    # 发送HTTP请求 - 设置更长的超时时间
    timeout_config = httpx.Timeout(180.0, connect=30.0)  # 总超时3分钟，连接超时30秒
    
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            print(f"📤 发送文生图请求...")
            print(f"⏱️ 超时配置: 总超时180秒，连接超时30秒")
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
                
                # 如果主接入点失败且未使用备用接入点，尝试备用接入点
                if not use_backup:
                    print(f"⚠️ 主接入点失败，尝试备用接入点...")
                    return await call_qiniu_image_gen_api(prompt, size, n, quality, style, True)
                
                return None
            
            print(f"✅ API调用成功!")
            data = r.json()
            return data
            
        except httpx.RequestError as e:
            print(f"❌(文生图服务) 网络请求失败: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            
            # 如果主接入点失败且未使用备用接入点，尝试备用接入点
            if not use_backup:
                print(f"⚠️ 主接入点失败，尝试备用接入点...")
                return await call_qiniu_image_gen_api(prompt, size, n, quality, style, True)
            
            return None
        except httpx.ReadTimeout as e:
            print(f"❌(文生图服务) 请求超时: {e}")
            # 超时也尝试备用接入点
            if not use_backup:
                print(f"⚠️ 主接入点超时，尝试备用接入点...")
                return await call_qiniu_image_gen_api(prompt, size, n, quality, style, True)
            return None
        except Exception as e:
            print(f"❌(文生图服务) API调用失败: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            return None


async def generate_image(prompt: str,
                        size: str = "1024x1024",
                        quality: str = "standard",
                        style: str = "vivid") -> Optional[Dict[str, Any]]:
    """
    生成单张图片
    
    功能说明：
    - 根据文字描述生成一张图片
    - 返回图片的base64数据
    
    参数：
        prompt: 图片描述文字
        size: 图片尺寸
        quality: 图片质量
        style: 图片风格
    
    返回：
        dict: {"url": "data:image/png;base64,...", "revised_prompt": "优化后的提示词"}
    """
    print(f"🎨(文生图服务) 开始生成图片...")
    print(f"   提示词: {prompt}")
    print(f"   尺寸: {size}")
    
    result = await call_qiniu_image_gen_api(prompt, size, 1, quality, style)
    
    if result and "data" in result and len(result["data"]) > 0:
        image_data = result["data"][0]
        print(f"✅(文生图服务) 图片生成成功")
        
        # 七牛云返回的是base64编码的图片数据
        b64_json = image_data.get("b64_json")
        if b64_json:
            # 转换为data URL格式，便于在浏览器中直接显示
            image_url = f"data:image/png;base64,{b64_json}"
            return {
                "url": image_url,
                "revised_prompt": image_data.get("revised_prompt", prompt)
            }
        else:
            print(f"❌(文生图服务) 响应中没有b64_json数据")
            return None
    else:
        print(f"❌(文生图服务) 图片生成失败")
        return None


async def generate_multiple_images(prompt: str,
                                   n: int = 4,
                                   size: str = "1024x1024",
                                   quality: str = "standard",
                                   style: str = "vivid") -> Optional[List[Dict[str, Any]]]:
    """
    生成多张图片
    
    功能说明：
    - 根据同一个文字描述生成多张图片
    - 提供多个选择供用户挑选
    
    参数：
        prompt: 图片描述文字
        n: 生成数量（1-10）
        size: 图片尺寸
        quality: 图片质量
        style: 图片风格
    
    返回：
        list: [{"url": "data:image/png;base64,..."}, {"url": "..."}, ...]
    """
    print(f"🎨(文生图服务) 开始批量生成图片...")
    print(f"   数量: {n} 张")
    
    if n < 1 or n > 10:
        print(f"❌ 生成数量必须在1-10之间")
        return None
    
    result = await call_qiniu_image_gen_api(prompt, size, n, quality, style)
    
    if result and "data" in result:
        images = []
        for img_data in result["data"]:
            # 七牛云返回的是base64编码的图片数据
            b64_json = img_data.get("b64_json")
            if b64_json:
                image_url = f"data:image/png;base64,{b64_json}"
                images.append({
                    "url": image_url,
                    "revised_prompt": img_data.get("revised_prompt", prompt)
                })
        print(f"✅(文生图服务) 成功生成 {len(images)} 张图片")
        return images if len(images) > 0 else None
    else:
        print(f"❌(文生图服务) 批量生成失败")
        return None


async def generate_image_variations(base_image_url: str,
                                    n: int = 4,
                                    size: str = "1024x1024") -> Optional[List[Dict[str, Any]]]:
    """
    生成图片变体（如果API支持）
    
    功能说明：
    - 基于一张参考图片生成变体
    - 保持相似风格但有所变化
    
    参数：
        base_image_url: 基础图片URL
        n: 生成变体数量
        size: 图片尺寸
    
    返回：
        list: 变体图片URL列表
    
    注意：此功能需要API支持，如不支持会返回None
    """
    print(f"🔄(文生图服务) 生成图片变体...")
    
    # 构建API请求参数
    payload = {
        "image": base_image_url,
        "n": n,
        "size": size
    }

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }

    url = f"{QINIU_API_BASE}/images/variations"
    
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            r = await client.post(url, headers=headers, json=payload)
            
            if r.status_code == 200:
                data = r.json()
                if "data" in data:
                    images = [{"url": img.get("url")} for img in data["data"]]
                    print(f"✅(文生图服务) 成功生成 {len(images)} 个变体")
                    return images
            else:
                print(f"⚠️(文生图服务) 图片变体功能不支持或失败")
                return None
                
        except Exception as e:
            print(f"⚠️(文生图服务) 图片变体功能异常: {e}")
            return None


async def generate_storyboard_images(scenes: List[Dict[str, str]],
                                     size: str = "1024x1024",
                                     style: str = "vivid") -> List[Dict[str, Any]]:
    """
    为分镜生成配图
    
    功能说明：
    - 为多个分镜场景批量生成图片
    - 适用于小说转漫画的场景
    - 每个场景生成一张配图
    
    参数：
        scenes: 场景列表，每项包含 {"index": 1, "description": "场景描述"}
        size: 图片尺寸
        style: 图片风格
    
    返回：
        list: [{"index": 1, "url": "图片URL", "description": "场景描述"}, ...]
    """
    print(f"🎬(文生图服务) 开始为分镜生成配图...")
    print(f"   场景数量: {len(scenes)}")
    
    results = []
    
    for i, scene in enumerate(scenes):
        scene_index = scene.get("index", i + 1)
        description = scene.get("description", "")
        
        print(f"🖼️ 生成第 {scene_index} 个场景配图...")
        
        # 优化提示词，适合漫画风格
        enhanced_prompt = f"漫画风格，高质量插图。{description}"
        
        result = await generate_image(enhanced_prompt, size, "standard", style)
        
        if result and result.get("url"):
            results.append({
                "index": scene_index,
                "url": result["url"],
                "description": description,
                "revised_prompt": result.get("revised_prompt")
            })
            print(f"✅ 第 {scene_index} 个场景配图完成")
        else:
            print(f"❌ 第 {scene_index} 个场景配图失败")
            results.append({
                "index": scene_index,
                "url": None,
                "description": description,
                "error": "生成失败"
            })
    
    success_count = sum(1 for r in results if r.get("url"))
    print(f"✅(文生图服务) 分镜配图完成，成功: {success_count}/{len(scenes)}")
    
    return results


def get_supported_sizes() -> List[str]:
    """
    获取支持的图片尺寸列表
    
    返回：
        list: 支持的尺寸列表
    """
    return [
        "256x256",    # 小尺寸，快速生成
        "512x512",    # 中等尺寸
        "1024x1024",  # 正方形，默认推荐
        "1792x1024",  # 横向宽屏
        "1024x1792"   # 竖向
    ]


def get_supported_styles() -> List[str]:
    """
    获取支持的图片风格列表
    
    返回：
        list: 支持的风格列表
    """
    return [
        "vivid",      # 生动、鲜艳、富有想象力
        "natural"     # 自然、真实、写实风格
    ]


def get_supported_qualities() -> List[str]:
    """
    获取支持的图片质量列表
    
    返回：
        list: 支持的质量列表
    """
    return [
        "standard",   # 标准质量，较快
        "hd"          # 高清质量，较慢但更精细
    ]

