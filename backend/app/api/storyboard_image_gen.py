# backend/app/api/storyboard_image_gen.py
#
# 分镜数据库图片生成API
# 
# 这个文件专门负责：
# 1. 从数据库读取分镜数据
# 2. 根据分镜字段生成提示词
# 3. 调用文生图API生成图片
# 4. 为每个分镜场景生成配图
#
# 设计原则：
# - 整合数据库和AI生成功能
# - 自动化分镜配图流程
# - 支持批量处理

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
import base64
import binascii
from datetime import datetime

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入服务层
from app.services import text_to_image
from app.services.comic_composer import add_dialogues_to_image
from app.db import db_client

# 创建路由器
router = APIRouter(prefix="/api/v1/storyboard-gen", tags=["Storyboard Image Generation"])


# ==================== 数据模型定义 ====================

class StoryboardImageRequest(BaseModel):
    """
    分镜图片生成请求模型
    """
    project_id: str                           # 项目ID
    storyboard_ids: Optional[List[str]] = None  # 分镜ID列表（可选，不提供则生成所有）
    size: str = "1024x1024"                   # 图片尺寸
    style: str = "vivid"                      # 图片风格


class SingleStoryboardImageRequest(BaseModel):
    """
    单个分镜图片生成请求
    """
    character_appearance: str                  # 角色外观描述
    scene_and_lighting: str                   # 场景和光线描述
    camera_and_composition: str               # 镜头和构图描述
    expression_and_action: str                # 表情和动作描述
    style_requirements: str                   # 风格要求
    size: str = "1024x1024"                   # 图片尺寸


# ==================== 辅助函数 ====================

async def save_image_to_local(image_base64: str, storyboard_id: str) -> str:
    """
    将base64格式的图片保存到本地layout文件夹并返回访问URL
    
    参数:
        image_base64: base64格式的图片数据（包含data:image/png;base64,前缀）
        storyboard_id: 分镜ID
    
    返回:
        str: 图片的HTTP访问URL
    """
    try:
        # 解析base64数据
        if ',' in image_base64:
            header, data = image_base64.split(',', 1)
            # 从header中提取图片格式
            if 'png' in header.lower():
                file_ext = '.png'
            elif 'jpg' in header.lower() or 'jpeg' in header.lower():
                file_ext = '.jpg'
            else:
                file_ext = '.png'
        else:
            data = image_base64
            file_ext = '.png'
        
        # 解码base64数据
        print(f"🔍 开始解码base64数据，数据长度: {len(data)}")
        print(f"🔍 base64前100字符: {data[:100]}")
        
        # -------------------
        # 💡 [解决方案] 修复Base64解码问题
        # -------------------
        # AI或PIL生成的Base64字符串可能缺少 = padding，导致b64decode失败
        # 我们需要手动添加padding，确保字符串长度是4的倍数
        try:
            # 尝试直接解码
            image_data = base64.b64decode(data)
        except (binascii.Error, ValueError, Exception) as e:
            # 如果解码失败，尝试修复padding
            print(f"⚠️ Base64解码失败，尝试修复padding: {e}")
            
            # 计算需要添加的padding数量（确保长度是4的倍数）
            padding_needed = (-len(data) % 4)
            if padding_needed:
                padding = '=' * padding_needed
                print(f"🔧 修复Base64 padding：添加 {padding_needed} 个 '=' 填充符")
                data_fixed = data + padding
                
                try:
                    # 再次尝试解码
                    image_data = base64.b64decode(data_fixed)
                    print(f"✅ 修复padding后解码成功")
                except Exception as e2:
                    print(f"❌ Base64解码失败 (已尝试修复padding): {e2}")
                    print(f"   失败的Base64数据长度: {len(data)}")
                    print(f"   失败的Base64数据 (前100字符): {data[:100]}...")
                    raise ValueError(f"Base64解码失败: {e2}") from e2
            else:
                # 不需要padding但仍然失败，说明数据本身有问题
                print(f"❌ Base64解码失败 (无需padding但仍然失败): {e}")
                print(f"   失败的Base64数据长度: {len(data)}")
                print(f"   失败的Base64数据 (前100字符): {data[:100]}...")
                raise ValueError(f"Base64解码失败: {e}") from e
        
        print(f"✅ base64解码成功，解码后数据长度: {len(image_data)} 字节")
        
        # 获取backend根目录的layout文件夹路径
        # __file__ 是 backend/app/api/storyboard_image_gen.py
        # dirname(dirname(dirname(__file__))) = backend目录
        backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        layout_dir = os.path.join(backend_root, "layout")
        
        # 确保layout目录存在
        if not os.path.exists(layout_dir):
            os.makedirs(layout_dir)
        
        # 生成文件名（使用storyboard_id和当前时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{storyboard_id}_{timestamp}{file_ext}"
        filepath = os.path.join(layout_dir, filename)
        
        # 保存图片
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # 返回HTTP访问URL
        image_url = f"http://127.0.0.1:8000/layout/{filename}"
        print(f"💾 图片已保存到: {filepath}")
        print(f"🌐 图片访问URL: {image_url}")
        
        return image_url
        
    except Exception as e:
        print(f"❌ 保存图片失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def _infer_dialogue_position(speaker_name: str, character_appearance: str, dialogue_index: int, total_dialogues: int) -> str:
    """
    根据角色在场景中的位置描述，智能推断对话框位置
    
    修改说明：
    - 解析 character_appearance 中的位置关键词
    - 根据角色的空间位置（左/右/前/后）推断对话框位置
    - 考虑对话顺序，避免重叠
    
    参数：
        speaker_name: 说话人名字
        character_appearance: 角色外观描述（如："闵峙坐在办公桌后,表情严肃;付柏启站在桌前"）
        dialogue_index: 当前对话的索引（从0开始）
        total_dialogues: 总对话数
    
    返回：
        str: 对话框位置（如 "top_right", "bottom_left"）
    """
    # 在描述中查找该角色的相关文本
    # 通常格式为："角色名...位置描述...;其他角色..."
    appearance_lower = character_appearance.lower()
    speaker_lower = speaker_name.lower()
    
    # 找到角色名称在描述中的位置
    if speaker_lower not in appearance_lower:
        return None
    
    # 提取该角色相关的描述片段（从角色名到下一个分号或结尾）
    start_idx = appearance_lower.find(speaker_lower)
    end_idx = character_appearance.find(';', start_idx)
    if end_idx == -1:
        end_idx = len(character_appearance)
    
    character_desc = character_appearance[start_idx:end_idx].lower()
    
    print(f"      🔍 分析位置描述: {character_desc[:40]}...")
    
    # 位置关键词映射
    # 右侧位置关键词（办公桌后、背后、右边等）
    right_keywords = ['办公桌后', '桌后', '后面', '背后', '右边', '右侧', '右方']
    # 左侧位置关键词（桌前、前面、左边等）
    left_keywords = ['桌前', '前面', '门口', '左边', '左侧', '左方', '站在桌前']
    
    # 判断水平位置
    is_right = any(keyword in character_desc for keyword in right_keywords)
    is_left = any(keyword in character_desc for keyword in left_keywords)
    
    # 判断垂直位置（根据对话顺序）
    # 第1个对话在上方，第2个在下方，以此类推
    is_top = (dialogue_index % 2 == 0)
    
    # 组合位置
    if is_right:
        position = "top_right" if is_top else "bottom_right"
        print(f"      ✅ 推断位置: 右侧 → {position}")
        return position
    elif is_left:
        position = "top_left" if is_top else "bottom_left"
        print(f"      ✅ 推断位置: 左侧 → {position}")
        return position
    else:
        # 没有明确位置关键词，使用默认分配
        print(f"      ⚪ 无明确位置关键词，使用默认分配")
        return None


def build_prompt_from_storyboard(data: dict) -> str:
    """
    根据分镜数据构建完整的提示词
    
    参数：
        data: 包含分镜字段的字典
    
    返回：
        str: 组合后的完整提示词
    """
    # 提取各个字段
    character = data.get("character_appearance", "")
    scene = data.get("scene_and_lighting", "")
    camera = data.get("camera_and_composition", "")
    expression = data.get("expression_and_action", "")
    style = data.get("style_requirements", "")
    
    # 强制添加漫画风格关键词，优先于用户指定的写实风格
    comic_style_prefix = "漫画风格, 日式漫画, 清晰的线条, 扁平化色彩"
    
    # 组合成完整的提示词
    prompt_parts = []
    
    if style:
        # 如果用户指定了写实风格，替换为漫画风格
        if any(word in style.lower() for word in ["写实", "真实", "realistic", "真实感"]):
            # 去掉写实相关描述
            style_modified = style
            for word in ["写实", "真实", "真实感", "realistic"]:
                style_modified = style_modified.replace(word, "")
            style_modified = style_modified.strip().rstrip(',')
            # 如果修改后不为空，添加漫画风格前缀
            if style_modified:
                prompt_parts.append(f"{comic_style_prefix}, {style_modified}")
            else:
                prompt_parts.append(comic_style_prefix)
        else:
            # 保留其他风格要求，但优先漫画风格
            prompt_parts.append(f"{comic_style_prefix}, {style}")
    else:
        # 如果没有指定风格，默认使用漫画风格
        prompt_parts.append(comic_style_prefix)
    
    if character:
        prompt_parts.append(f"角色: {character}")
    
    if scene:
        prompt_parts.append(f"场景: {scene}")
    
    if camera:
        prompt_parts.append(f"镜头: {camera}")
    
    if expression:
        prompt_parts.append(f"表情动作: {expression}")
    
    # 用逗号连接所有部分
    prompt = ", ".join(prompt_parts)
    
    print(f"🎨 构建的提示词: {prompt[:100]}...")
    return prompt


async def parse_panel_elements_dialogues(db_client, panel_elements_data, character_appearance=""):
    """
    解析 panel_elements 字段中的对话数据，并关联 characters 表
    
    修改说明：
    - 从 panel_elements (jsonb) 字段读取对话数据
    - 提取每个对话的 dialogue 和 characterid
    - 通过 characterid 查询 characters 表获取角色名称
    - 根据 character_appearance 描述智能推断对话框位置
    - 返回包含角色名称、对话内容和位置的结构化数据
    
    参数：
        conn: 数据库连接
        panel_elements_data: panel_elements 字段的 jsonb 数据
        character_appearance: 角色外观描述（用于推断位置）
    
    返回：
        list: 对话列表，每个元素包含 {speaker, text, bubble_type, position}
    """
    if not panel_elements_data:
        return []
    
    dialogues = []
    
    try:
        # panel_elements 是一个数组，每个元素是一个对话对象
        # 格式: [{"dialogue": "...", "characterid": "...", ...}, ...]
        import json
        
        # 如果是字符串，先解析
        if isinstance(panel_elements_data, str):
            panel_elements = json.loads(panel_elements_data)
        else:
            panel_elements = panel_elements_data
        
        print(f"📝 解析 panel_elements，共 {len(panel_elements)} 个元素")
        print(f"📍 角色位置描述: {character_appearance[:50]}..." if character_appearance else "📍 无角色位置描述")
        
        for idx, element in enumerate(panel_elements):
            dialogue_text = element.get("dialogue", "").strip()
            # 修改说明：支持两种格式 character_id（有下划线）和 characterid（无下划线）
            character_id = element.get("character_id") or element.get("characterid")
            
            if not dialogue_text:
                continue
            
            # 查询角色名称
            speaker_name = "旁白"  # 默认说话人
            if character_id:
                try:
                    char_result = (db_client.client.table('characters')
                                  .select('name')
                                  .eq('character_id', character_id)
                                  .execute())
                    if char_result.data and len(char_result.data) > 0:
                        speaker_name = char_result.data[0]['name']
                        print(f"   ✅ 找到角色: {speaker_name} (ID: {character_id})")
                    else:
                        print(f"   ⚠️ 未找到角色ID: {character_id}，使用默认")
                        print(f"   💡 请检查 characters 表中是否存在这个ID")
                except Exception as e:
                    print(f"   ❌ 查询角色失败: {e}")
            
            # 智能推断对话框位置
            # 修改说明：根据角色在场景中的位置描述，智能分配对话框位置
            position = None
            if character_appearance and speaker_name != "旁白":
                position = _infer_dialogue_position(speaker_name, character_appearance, idx, len(panel_elements))
                if position:
                    print(f"   📍 根据位置描述推断: {speaker_name} → {position}")
            
            # 构建对话数据
            dialogue_data = {
                "speaker": speaker_name,
                "text": dialogue_text,
                "bubble_type": "speech"  # 可以根据内容智能判断类型
            }
            
            # 如果推断出了位置，添加到数据中
            if position:
                dialogue_data["position"] = position
            
            dialogues.append(dialogue_data)
            
            print(f"   💬 {speaker_name}: {dialogue_text[:30]}...")
        
        print(f"✅ 成功解析 {len(dialogues)} 条对话")
        return dialogues
        
    except Exception as e:
        print(f"❌ 解析 panel_elements 失败: {e}")
        import traceback
        traceback.print_exc()
        return []


# ==================== API接口定义 ====================

@router.get("/list-storyboards")
async def list_storyboards(limit: int = 10, offset: int = 0):
    """
    列出数据库中的分镜数据（用于测试）
    
    参数：
        limit: 返回的最大记录数（默认10）
        offset: 偏移量，用于分页（默认0）
    
    返回：
        dict: 包含分镜数据列表和总数
    
    修改说明：
    - 添加了 offset 参数支持分页查询
    - count 字段返回数据库总记录数，而不是当前查询到的记录数
    - 适配前端的分页功能，每页10条数据
    """
    print(f"📊(API) 查询数据库分镜列表 (limit={limit}, offset={offset})")
    
    # 检查数据库连接
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 使用 Supabase 客户端查询
        if not db_client.is_connected:
            raise HTTPException(status_code=500, detail="数据库未连接")
        
        # 查询总数
        count_result = db_client.client.table('storyboards').select('*', count='exact').execute()
        total_count = count_result.count
        
        # 查询分页数据
        result = (db_client.client.table('storyboards')
                 .select('*')
                 .order('created_at', desc=True)
                 .limit(limit)
                 .offset(offset)
                 .execute())
        
        storyboards = result.data if result.data else []
        
        print(f"✅ 查询到 {len(storyboards)} 条分镜数据（总共 {total_count} 条）")
        
        return {
            "ok": True,
            "count": total_count,
            "storyboards": storyboards,
            "current_page_count": len(storyboards),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        print(f"❌(API) 查询失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/storyboard/{storyboard_id}")
async def get_storyboard(storyboard_id: str):
    """
    获取单个分镜数据
    
    参数：
        storyboard_id: 分镜ID
    
    返回：
        dict: 分镜数据
    """
    print(f"📊(API) 查询分镜数据: {storyboard_id}")
    
    # 检查数据库连接
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 使用 Supabase 客户端查询
        result = (db_client.client.table('storyboards')
                 .select('*')
                 .eq('storyboard_id', storyboard_id)
                 .execute())
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="分镜数据不存在")
        
        storyboard = result.data[0]
        print(f"✅ 查询到分镜数据")
        
        return {
            "ok": True,
            "storyboard": storyboard
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/generate-from-db/{storyboard_id}")
async def generate_from_database_id(storyboard_id: str, size: str = "1024x1024"):
    """
    从数据库读取指定分镜并生成图片
    
    功能说明：
    - 从数据库读取指定ID的分镜数据
    - 自动组合各字段生成提示词
    - 生成配图
    
    参数：
        storyboard_id: 分镜ID
        size: 图片尺寸
    
    返回：
        dict: 包含生成的图片
    """
    print(f"📊(API) 从数据库生成分镜图片")
    print(f"   分镜ID: {storyboard_id}")
    
    # 检查数据库连接
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 1. 从数据库读取分镜数据
        result = (db_client.client.table('storyboards')
                 .select('*')
                 .eq('storyboard_id', storyboard_id)
                 .execute())
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="分镜数据不存在")
        
        storyboard_data = result.data[0]
        print(f"✅ 查询到分镜数据")
        
        # 2. 构建提示词
        prompt = build_prompt_from_storyboard({
            "character_appearance": storyboard_data.get("character_appearance", ""),
            "scene_and_lighting": storyboard_data.get("scene_and_lighting", ""),
            "camera_and_composition": storyboard_data.get("camera_and_composition", ""),
            "expression_and_action": storyboard_data.get("expression_and_action", ""),
            "style_requirements": storyboard_data.get("style_requirements", "")
        })
        
        print(f"📝 完整提示词: {prompt}")
        
        # 3. 调用文生图服务（生成纯画面，不含文字）
        result = await text_to_image.generate_image(
            prompt=prompt,
            size=size,
            quality="standard",
            style="vivid"
        )
        
        if result:
            print(f"✅(API) 分镜图片生成成功，图片URL长度: {len(result.get('url', '')) if result.get('url') else 0}")
            
            # 4. 自动添加对话框（从 panel_elements 字段读取）
            # 修改说明：
            # - 从 panel_elements (jsonb) 字段读取对话数据
            # - 通过 characterid 关联 characters 表获取角色名称
            # - 根据 character_appearance 智能推断对话框位置
            # - 将角色名称和对话内容组合后渲染到图片上
            panel_elements_data = storyboard_data.get("panel_elements")
            character_appearance = storyboard_data.get("character_appearance", "")
            camera_angle = storyboard_data.get("camera_and_composition", "")
            
            final_image = result
            dialogues = []
            
            if panel_elements_data:
                print(f"🎨 开始解析 panel_elements 对话数据...")
                
                # 使用数据库连接解析对话数据（传入角色位置描述）
                # 传递 db_client 以便查询角色信息
                dialogues = await parse_panel_elements_dialogues(db_client, panel_elements_data, character_appearance)
                
                if dialogues:
                    print(f"🎨 开始添加 {len(dialogues)} 个对话框...")
                    
                    # 调用漫画合成器添加对话框
                    try:
                        final_image_with_dialogue = add_dialogues_to_image(
                            image_base64=result["url"],
                            dialogues=dialogues,
                            camera_angle=camera_angle
                        )
                        
                        # 更新result中的图片URL（先保持base64格式，后面统一保存）
                        final_image = {
                            "url": final_image_with_dialogue,
                            "revised_prompt": result.get("revised_prompt", prompt)
                        }
                        
                        print(f"✅ 对话框添加成功")
                    except Exception as e:
                        print(f"⚠️ 对话框添加失败，返回原图: {e}")
                        import traceback
                        traceback.print_exc()
                        # 如果添加对话框失败，仍然返回原图
                else:
                    print(f"ℹ️ panel_elements 中无有效对话内容")
            else:
                print(f"ℹ️ 无 panel_elements 数据，返回纯画面")
            
            # 将图片（无论是否有对话框）保存到本地
            # 我们需要这一步，因为Base64太大了，通过代理访问本地文件
            if final_image.get("url"):
                try:
                    image_url = await save_image_to_local(
                        final_image["url"],
                        storyboard_id
                    )
                    # 更新为本地URL
                    final_image["url"] = image_url
                except Exception as e:
                    print(f"⚠️ 保存图片失败，返回原URL: {e}")
            
            response_data = {
                "ok": True,
                "storyboard_id": storyboard_id,
                "storyboard_data": {
                    "original_text_snippet": storyboard_data.get("original_text_snippet", ""),
                    "character_appearance": storyboard_data.get("character_appearance", ""),
                    "scene_and_lighting": storyboard_data.get("scene_and_lighting", ""),
                    "camera_and_composition": storyboard_data.get("camera_and_composition", ""),
                    "expression_and_action": storyboard_data.get("expression_and_action", ""),
                    "style_requirements": storyboard_data.get("style_requirements", ""),
                    "panel_elements": panel_elements_data
                },
                "dialogues": dialogues,  # 新增：包含解析后的对话列表（含角色名称）
                "dialogue_count": len(dialogues),
                "prompt_used": prompt,
                "image": final_image,
                "has_dialogue": len(dialogues) > 0,
                "message": "分镜图片生成成功" + (f"（已添加 {len(dialogues)} 个对话框）" if dialogues else "")
            }
            
            print(f"📤 返回数据: has_dialogue={response_data['has_dialogue']}, dialogue_count={len(dialogues)}")
            print(f"📤 图片URL类型: {type(final_image.get('url') if final_image else None)}")
            
            return response_data
        else:
            print(f"❌(API) 分镜图片生成失败，result为None")
            print(f"🔍 可能的原因：API超时、网络问题或API配置错误")
            raise HTTPException(status_code=500, detail="图片生成失败，请检查API配置或稍后重试")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 从数据库生成失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/generate-from-fields")
async def generate_from_fields(req: SingleStoryboardImageRequest):
    """
    根据分镜字段直接生成图片
    
    功能说明：
    - 接收分镜的各个字段
    - 自动组合成提示词
    - 生成对应的图片
    
    使用场景：
    - 测试分镜描述的视觉效果
    - 快速预览分镜配图
    
    参数：
        req: SingleStoryboardImageRequest - 包含所有分镜描述字段
    
    返回：
        dict: 包含生成的图片
    """
    print(f"🎨(API) 根据字段生成分镜图片")
    
    try:
        # 1. 构建提示词
        prompt = build_prompt_from_storyboard({
            "character_appearance": req.character_appearance,
            "scene_and_lighting": req.scene_and_lighting,
            "camera_and_composition": req.camera_and_composition,
            "expression_and_action": req.expression_and_action,
            "style_requirements": req.style_requirements
        })
        
        print(f"📝 完整提示词: {prompt}")
        
        # 2. 调用文生图服务
        result = await text_to_image.generate_image(
            prompt=prompt,
            size=req.size,
            quality="standard",
            style="vivid"
        )
        
        if result:
            print(f"✅(API) 分镜图片生成成功")
            return {
                "ok": True,
                "image": result,
                "prompt_used": prompt,
                "message": "分镜图片生成成功"
            }
        else:
            print(f"❌(API) 分镜图片生成失败")
            raise HTTPException(status_code=500, detail="图片生成失败")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌(API) 生成异常: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/test-prompt-build")
async def test_prompt_build(req: SingleStoryboardImageRequest):
    """
    测试提示词构建（不生成图片）
    
    功能说明：
    - 只构建提示词，不调用AI生成
    - 用于测试提示词组合效果
    
    参数：
        req: SingleStoryboardImageRequest
    
    返回：
        dict: 包含构建的提示词
    """
    prompt = build_prompt_from_storyboard({
        "character_appearance": req.character_appearance,
        "scene_and_lighting": req.scene_and_lighting,
        "camera_and_composition": req.camera_and_composition,
        "expression_and_action": req.expression_and_action,
        "style_requirements": req.style_requirements
    })
    
    return {
        "ok": True,
        "prompt": prompt,
        "field_breakdown": {
            "style_requirements": req.style_requirements,
            "character_appearance": req.character_appearance,
            "scene_and_lighting": req.scene_and_lighting,
            "camera_and_composition": req.camera_and_composition,
            "expression_and_action": req.expression_and_action
        }
    }


@router.get("/health")
async def health_check():
    """
    分镜图片生成服务健康检查
    """
    return {
        "ok": True,
        "service": "分镜图片生成服务",
        "database_connected": db_client.is_connected if hasattr(db_client, 'is_connected') else False,
        "message": "服务正常运行"
    }

