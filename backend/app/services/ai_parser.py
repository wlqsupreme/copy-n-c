# backend/app/services/ai_parser.py
# 
# AI服务层 - 小说解析和分镜生成的核心逻辑
# 
# 这个文件专门负责：
# 1. 调用七牛云AI API进行文本处理
# 2. 智能分段：将长篇小说按情节节点分段
# 3. 分镜生成：将文本转换为漫画分镜结构
# 4. 错误处理和降级策略
#
# 设计原则：
# - 纯业务逻辑，不涉及HTTP请求/响应
# - 不直接操作数据库，通过上层API调用
# - 可独立测试和复用
# - 为协作者预留扩展空间（如文生图功能）

import httpx
import json
import re
import os
import sys
from typing import List, Dict, Any

# 添加 backend 目录到 Python 路径，确保能导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config

# 七牛云OpenAI兼容API入口
QINIU_API_BASE = "https://openai.qiniu.com/v1"


async def call_qiniu_api(messages: list) -> dict:
    """
    调用七牛云AI API的通用函数
    
    功能说明：
    - 统一的API调用接口，处理所有与七牛云AI的交互
    - 自动处理认证、超时、错误重试等
    - 智能解析AI返回的JSON内容
    
    参数：
        messages: OpenAI格式的消息列表，包含system和user prompt
    
    返回：
        dict: 解析后的JSON数据，失败时返回None
    """
    # 构建API请求参数
    payload = {
        "model": config.model,           # AI模型名称
        "messages": messages,            # 对话消息
        "max_tokens": config.max_tokens, # 最大生成token数
        "temperature": config.temperature # 创造性程度
    }

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }

    url = f"{QINIU_API_BASE}/chat/completions"
    
    print(f"🚀(AI服务) 开始调用七牛云API...")
    print(f"📡 URL: {url}")
    print(f"🤖 模型: {config.model}")
    print(f"📝 消息数量: {len(messages)}")
    print(f"🔑 API Key: {config.api_key[:10]}...{config.api_key[-10:] if len(config.api_key) > 20 else config.api_key}")

    # 发送HTTP请求
    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            print(f"📤 发送请求...")
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
            print(f"❌(AI服务) 网络请求失败: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            return None
        except Exception as e:
            print(f"❌(AI服务) API调用失败: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            return None

    # 智能解析AI返回的内容
    try:
        # 尝试从标准OpenAI响应格式中提取内容
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            # 兼容其他可能的响应格式
            content = data.get("choices", [{}])[0].get("text") or data.get("payload") or json.dumps(data)
    except Exception:
        content = json.dumps(data)

    # 尝试解析content为JSON
    parsed = None
    try:
        parsed = json.loads(content)
    except Exception:
        # AI可能返回文本中包含JSON，尝试提取第一个 {...}
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:
                parsed = None

    return parsed


async def generate_storyboard_for_segment(
    segment_text: str, 
    title: str, 
    segment_index: int,
    existing_characters: List[Dict[str, Any]] = None
) -> dict:
    """
    为单个文本段生成分镜和角色信息（感知项目上下文）
    
    功能说明：
    - 将小说文本转换为漫画分镜结构
    - 感知项目中已存在的角色，避免重复生成
    - 只生成新角色的基础描述，已存在角色只生成情景外貌
    - 考虑镜头构图、人物表情、场景描述等要素
    - 生成标准化的JSON格式，包含characters和storyboards列表
    
    参数：
        segment_text: 要处理的文本段落
        title: 小说标题（用于上下文）
        segment_index: 段落序号
        existing_characters: 该项目已存在的角色列表
    
    返回：
        dict: 包含characters和storyboards的字典
    """
    print(f"🎬(AI服务) 开始生成分镜和角色信息 (段落 {segment_index})...")
    print(f"   文本长度: {len(segment_text)} 字符")
    
    # 序列化已存在的角色列表
    existing_chars_json = "[]"
    if existing_characters:
        try:
            existing_chars_json = json.dumps(existing_characters, ensure_ascii=False)
            print(f"   感知到 {len(existing_characters)} 个已存在的角色。")
        except Exception:
            pass  # 即使失败，也使用空列表
    
    # 构建AI提示词
    system_prompt = f"""你是一个专业的分镜脚本生成器。

本项目已经定义了以下角色：
{existing_chars_json}

你的任务是：
1. **分析用户文本**：阅读用户提供的文本片段。
2. **生成分镜 (storyboards)**：
   * 为文本生成详细的分镜面板。
   * `character_name` 必须与角色名称匹配。
   * `character_appearance` 必须生成，描述该分镜中角色的*特定*外貌、穿着或表情（例如"衣服破损"、"泪流满面"）。
3. **识别新角色 (characters)**：
   * **仅当**文本中出现了*不在*上面"本项目已经定义的角色"列表中的**新角色**时，才在`characters`数组中添加该角色的基础描述（`description`）。
   * 如果文本中的角色都*已存在*于列表中，请返回一个**空**的`characters`数组 ( `[]` )。

请严格按照以下JSON格式返回数据：
{{
  "characters": [
    {{
      "name": "新角色名称",
      "description": "该新角色的详细基础描述 (年龄, 性别, 身高...)"
    }}
  ],
  "storyboards": [
    {{
      "original_text_snippet": "该分镜对应的原始文本片段",
      "character_name": "主要角色名称 (必须是已存在或新角色)",
      "character_appearance": "该分镜中角色的*情景*外貌描述",
      "scene_and_lighting": "场景与光照描述",
      "camera_and_composition": "镜头与构图描述",
      "expression_and_action": "表情与动作描述",
      "style_requirements": "风格要求描述"
    }}
  ]
}}"""
    
    messages = [
        {
            "role": "system", 
            "content": system_prompt
        },
        {
            "role": "user", 
            "content": f"标题: {title or ''}\n段落 {segment_index}:\n{segment_text}\n\n请根据以上规则，生成分镜和角色信息的JSON数据。"
        }
    ]
    
    # 调用AI API生成分镜
    result = await call_qiniu_api(messages)
    if result and "storyboards" in result:
        # 确保 characters 键存在，即使AI返回了null或漏掉了
        if "characters" not in result:
            result["characters"] = []
            
        print(f"✅(AI服务) 分镜和角色生成成功")
        print(f"   识别到新角色数量: {len(result['characters'])}")
        print(f"   生成分镜数量: {len(result['storyboards'])}")
        return result
    else:
        print(f"❌(AI服务) 分镜和角色生成失败")
        return {"characters": [], "storyboards": []}


def simple_text_segment(text: str) -> list:
    """
    简单的文本分段规则（AI分段失败时的降级方案）
    
    功能说明：
    - 当AI智能分段失败时使用的备用方案
    - 按段落和字数进行简单分割
    - 确保每段控制在合理长度内
    
    参数：
        text: 要分段的完整文本
    
    返回：
        list: 分段列表，每段包含segment_index、content、summary
    """
    segments = []
    # 按双换行符分割段落
    paragraphs = text.split('\n\n')
    current_segment = ""
    segment_index = 1
    
    for para in paragraphs:
        # 如果当前段落加上新段落超过1000字，就结束当前段
        if len(current_segment + para) > 1000 and current_segment:
            segments.append({
                "segment_index": segment_index,
                "content": current_segment.strip(),
                "summary": current_segment[:100] + "..."
            })
            current_segment = para
            segment_index += 1
        else:
            # 否则继续累积段落
            current_segment += "\n\n" + para if current_segment else para
    
    # 处理最后一段
    if current_segment:
        segments.append({
            "segment_index": segment_index,
            "content": current_segment.strip(),
            "summary": current_segment[:100] + "..."
        })
    
    return segments


async def segment_text(text: str, existing_characters: List[Dict[str, Any]] = None) -> list:
    """
    将长文本进行智能分段
    
    功能说明：
    - 优先使用AI进行智能分段，按情节发展、场景转换等自然节点分段
    - AI失败时自动降级到规则分段
    - 确保每段控制在800-1200字左右，保持情节完整性
    
    参数：
        text: 要分段的完整小说文本
    
    返回：
        list: 分段列表，每段包含segment_index、content、summary
    """
    print(f"📝(AI服务) 开始AI智能分段...")
    
    # 构建AI分段提示词
    messages = [
        {
            "role": "system", 
            "content": """你是一个文本分段专家。将长篇小说文本按照情节发展、场景转换、人物对话等自然节点进行分段。每段控制在800-1200字左右，保持情节完整性。返回JSON格式：{"segments": [{"segment_index": int, "content": str, "summary": str}]}"""
        },
        {
            "role": "user", 
            "content": f"请将以下文本分段：\n\n{text}"
        }
    ]
    
    # 尝试AI智能分段
    result = await call_qiniu_api(messages)
    if result and "segments" in result:
        print(f"✅(AI服务) AI分段成功，生成 {len(result['segments'])} 段")
        return result["segments"]
    else:
        # AI分段失败，使用规则分段作为降级方案
        print(f"⚠️(AI服务) AI分段失败，使用规则分段...")
        segments = simple_text_segment(text)
        print(f"✅(AI服务) 规则分段完成，生成 {len(segments)} 段")
        return segments
