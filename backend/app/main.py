import os
import json
import asyncio
from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from database import db_manager

QINIU_API_BASE = "https://openai.qiniu.com/v1"  # 七牛 openai 兼容入口

# 检查配置是否有效
if not config.is_valid():
    print(config.get_error_message())
    sys.exit(1)

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    print("🚀 应用启动中...")
    if config.is_database_configured():
        success = await db_manager.connect()
        if success:
            await db_manager.init_tables()
    else:
        print("⚠️ 数据库未配置，跳过数据库初始化")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    print("🛑 应用关闭中...")
    await db_manager.close()


class ParseRequest(BaseModel):
    title: str | None = None
    text: str
    auto_segment: bool = True  # 是否自动分段


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/parse")
async def parse_text(req: ParseRequest):
    """
    接收小说文本，调用七牛云 AI 接口生成结构化分镜 JSON。
    支持长文本自动分段处理。
    """
    print(f"📖 收到解析请求:")
    print(f"   标题: {req.title}")
    print(f"   文本长度: {len(req.text)} 字符")
    print(f"   自动分段: {req.auto_segment}")
    
    # 如果启用自动分段且文本较长，先进行分段
    if req.auto_segment and len(req.text) > 1000:
        print(f"🔄 开始长文本分段处理...")
        segments = await segment_text(req.text)
        print(f"📝 分段完成，共 {len(segments)} 段")
        
        all_pages = []
        
        for i, segment in enumerate(segments):
            print(f"🎬 处理第 {i+1} 段...")
            pages = await generate_storyboard_for_segment(segment, req.title, i + 1)
            all_pages.extend(pages)
            print(f"✅ 第 {i+1} 段完成，生成 {len(pages)} 页")
        
        print(f"🎉 所有分段处理完成，共生成 {len(all_pages)} 页")
        return {"ok": True, "storyboard": {"pages": all_pages}, "segments_count": len(segments)}
    else:
        print(f"🎬 直接处理短文本...")
        # 直接处理短文本
        pages = await generate_storyboard_for_segment(req.text, req.title, 1)
        print(f"✅ 短文本处理完成，生成 {len(pages)} 页")
        return {"ok": True, "storyboard": {"pages": pages}}


async def segment_text(text: str) -> list:
    """将长文本分段"""
    print(f"📝 开始AI智能分段...")
    messages = [
        {"role": "system", "content": "你是一个文本分段专家。将长篇小说文本按照情节发展、场景转换、人物对话等自然节点进行分段。每段控制在800-1200字左右，保持情节完整性。返回JSON格式：{\"segments\": [{\"segment_index\": int, \"content\": str, \"summary\": str}]}"},
        {"role": "user", "content": f"请将以下文本分段：\n\n{text}"}
    ]
    
    result = await call_qiniu_api(messages)
    if result and "segments" in result:
        print(f"✅ AI分段成功，生成 {len(result['segments'])} 段")
        return result["segments"]
    else:
        print(f"⚠️ AI分段失败，使用规则分段...")
        # 如果AI分段失败，使用简单规则分段
        segments = simple_text_segment(text)
        print(f"✅ 规则分段完成，生成 {len(segments)} 段")
        return segments


async def generate_storyboard_for_segment(segment_text: str, title: str, segment_index: int) -> list:
    """为单个文本段生成分镜"""
    print(f"🎬 开始生成分镜 (段落 {segment_index})...")
    print(f"   文本长度: {len(segment_text)} 字符")
    
    messages = [
        {"role": "system", "content": "你是一个专业的分镜脚本生成器。根据小说文本生成漫画分镜，考虑以下要素：\n1. 剧情节点和节奏\n2. 镜头构图（近景/中景/远景/特写）\n3. 人物表情和动作\n4. 场景描述\n5. 对话气泡位置\n\n返回严格JSON格式：{\"pages\": [{\"page_index\": int, \"panels\": [{\"panel_index\": int, \"description\": str, \"characters\": [str], \"dialogue\": [str], \"camera_angle\": str, \"emotion\": str}]}]}"},
        {"role": "user", "content": f"标题: {title or ''}\n段落 {segment_index}:\n{segment_text}\n\n请生成分镜JSON，每页3-6个panel。"}
    ]
    
    result = await call_qiniu_api(messages)
    if result and "pages" in result:
        print(f"✅ 分镜生成成功，生成 {len(result['pages'])} 页")
        return result["pages"]
    else:
        print(f"❌ 分镜生成失败")
        return []


def simple_text_segment(text: str) -> list:
    """简单的文本分段规则"""
    segments = []
    # 按段落分割
    paragraphs = text.split('\n\n')
    current_segment = ""
    segment_index = 1
    
    for para in paragraphs:
        if len(current_segment + para) > 1000 and current_segment:
            segments.append({
                "segment_index": segment_index,
                "content": current_segment.strip(),
                "summary": current_segment[:100] + "..."
            })
            current_segment = para
            segment_index += 1
        else:
            current_segment += "\n\n" + para if current_segment else para
    
    if current_segment:
        segments.append({
            "segment_index": segment_index,
            "content": current_segment.strip(),
            "summary": current_segment[:100] + "..."
        })
    
    return segments


async def call_qiniu_api(messages: list) -> dict:
    """调用七牛云API的通用函数"""
    payload = {
        "model": config.model,
        "messages": messages,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature
    }

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }

    url = f"{QINIU_API_BASE}/chat/completions"
    
    print(f"🚀 开始调用七牛云API...")
    print(f"📡 URL: {url}")
    print(f"🤖 模型: {config.model}")
    print(f"📝 消息数量: {len(messages)}")
    print(f"🔑 API Key: {config.api_key[:10]}...{config.api_key[-10:] if len(config.api_key) > 20 else config.api_key}")

    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            print(f"📤 发送请求...")
            r = await client.post(url, headers=headers, json=payload)
            print(f"📥 收到响应: {r.status_code}")
        except httpx.RequestError as e:
            print(f"❌ 网络请求失败: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            return None
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            return None

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
    
    # 尝试从 data 中抽取文本内容
    try:
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            content = data.get("choices", [{}])[0].get("text") or data.get("payload") or json.dumps(data)
    except Exception:
        content = json.dumps(data)

    # 尝试解析 content 为 JSON
    parsed = None
    try:
        parsed = json.loads(content)
    except Exception:
        # 模型可能返回文本里带 JSON，尝试提取首个 {...}
        import re
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:
                parsed = None

    return parsed
