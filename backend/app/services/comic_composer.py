# backend/app/services/comic_composer.py
#
# 漫画合成服务
# 
# 功能：
# 1. 在AI生成的图片上自动添加对话框
# 2. 智能定位对话框位置
# 3. 渲染专业的漫画文字效果
# 4. 支持多种对话框样式
#
# 核心理念：
# - 图文分离：AI只生成画面，文字后期添加
# - 自动布局：根据规则自动定位对话框
# - 专业效果：使用漫画专业字体和样式

from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, Optional
import io
import base64
import os


class DialoguePosition:
    """对话框位置预设"""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_CENTER = "middle_center"
    MIDDLE_RIGHT = "middle_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class BubbleType:
    """对话框类型"""
    SPEECH = "speech"          # 普通对话
    THOUGHT = "thought"        # 心理活动
    CAPTION = "caption"        # 旁白
    SHOUT = "shout"           # 大喊
    WHISPER = "whisper"       # 低语
    SFX = "sfx"               # 音效


class ComicComposer:
    """漫画合成器"""
    
    def __init__(self):
        # 字体配置（支持中文）
        # 尝试加载系统中文字体
        self.font_paths = self._find_chinese_fonts()
        
        # 对话框样式配置
        self.bubble_config = {
            BubbleType.SPEECH: {
                "bg_color": (255, 255, 255, 230),  # 白色半透明
                "border_color": (0, 0, 0, 255),     # 黑色边框
                "border_width": 3,
                "padding": 20,
                "corner_radius": 15
            },
            BubbleType.THOUGHT: {
                "bg_color": (255, 255, 255, 200),
                "border_color": (100, 100, 100, 255),
                "border_width": 2,
                "padding": 20,
                "corner_radius": 25
            },
            BubbleType.CAPTION: {
                "bg_color": (0, 0, 0, 200),         # 黑色半透明
                "border_color": (255, 255, 255, 255),
                "border_width": 2,
                "padding": 15,
                "corner_radius": 5
            }
        }
        
        print("✅ 漫画合成器初始化完成")
    
    def _find_chinese_fonts(self) -> Dict[str, str]:
        """查找系统中的中文字体"""
        font_paths = {}
        
        # Windows字体路径
        windows_fonts = [
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "C:/Windows/Fonts/simsun.ttc",    # 宋体
        ]
        
        # 检查哪些字体存在
        for font_path in windows_fonts:
            if os.path.exists(font_path):
                if "msyh" in font_path:
                    font_paths["normal"] = font_path
                elif "simhei" in font_path:
                    font_paths["bold"] = font_path
                else:
                    font_paths["fallback"] = font_path
        
        # 如果没有找到任何字体，使用默认字体
        if not font_paths:
            print("⚠️ 未找到中文字体，将使用系统默认字体")
            font_paths["normal"] = None
        
        return font_paths
    
    def _get_font(self, size: int = 24, bold: bool = False) -> ImageFont.FreeTypeFont:
        """获取字体对象"""
        try:
            font_key = "bold" if bold else "normal"
            font_path = self.font_paths.get(font_key) or self.font_paths.get("normal")
            
            if font_path:
                return ImageFont.truetype(font_path, size)
            else:
                # 使用默认字体
                return ImageFont.load_default()
        except Exception as e:
            print(f"⚠️ 字体加载失败: {e}")
            return ImageFont.load_default()
    
    def _calculate_bubble_position(
        self, 
        image_size: Tuple[int, int], 
        position: str, 
        bubble_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        计算对话框位置
        
        参数:
            image_size: 图片尺寸 (width, height)
            position: 位置预设 (如 "top_left")
            bubble_size: 对话框尺寸 (width, height)
        
        返回:
            (x, y): 对话框左上角坐标
        """
        img_w, img_h = image_size
        bubble_w, bubble_h = bubble_size
        
        # 边距（修改说明：保持合理边距，对话框在边角位置）
        # margin 是对话框与图片边缘的距离
        # 较小的 margin = 更贴近边缘 = 更不遮挡中心人物
        margin = 20  # 从30减少到20，让对话框更贴近边缘
        
        # 位置映射
        position_map = {
            DialoguePosition.TOP_LEFT: (margin, margin),
            DialoguePosition.TOP_CENTER: ((img_w - bubble_w) // 2, margin),
            DialoguePosition.TOP_RIGHT: (img_w - bubble_w - margin, margin),
            
            DialoguePosition.MIDDLE_LEFT: (margin, (img_h - bubble_h) // 2),
            DialoguePosition.MIDDLE_CENTER: ((img_w - bubble_w) // 2, (img_h - bubble_h) // 2),
            DialoguePosition.MIDDLE_RIGHT: (img_w - bubble_w - margin, (img_h - bubble_h) // 2),
            
            DialoguePosition.BOTTOM_LEFT: (margin, img_h - bubble_h - margin),
            DialoguePosition.BOTTOM_CENTER: ((img_w - bubble_w) // 2, img_h - bubble_h - margin),
            DialoguePosition.BOTTOM_RIGHT: (img_w - bubble_w - margin, img_h - bubble_h - margin),
        }
        
        return position_map.get(position, (margin, margin))
    
    def _auto_position_dialogues(
        self,
        image_size: Tuple[int, int],
        dialogue_count: int,
        camera_angle: Optional[str] = None
    ) -> List[str]:
        """
        自动分配对话框位置
        
        修改说明：
        - 优先使用边角位置（TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT）
        - 避免使用中央位置（CENTER），减少遮挡人脸
        - 对话框对角分布，更美观且避开画面中心
        
        根据镜头角度和对话数量，智能分配位置
        
        参数:
            image_size: 图片尺寸
            dialogue_count: 对话数量
            camera_angle: 镜头角度
        
        返回:
            位置列表
        """
        # 根据对话数量自动布局（优先使用边角位置）
        if dialogue_count == 1:
            # 单个对话：放在顶部左角（避开中央）
            return [DialoguePosition.TOP_LEFT]
        
        elif dialogue_count == 2:
            # 两个对话：对角分布（左上 + 右下）
            # 这样可以最大程度避免遮挡画面中央的人物
            return [DialoguePosition.TOP_LEFT, DialoguePosition.BOTTOM_RIGHT]
        
        elif dialogue_count == 3:
            # 三个对话：三角分布（左上、右上、左下）
            return [
                DialoguePosition.TOP_LEFT,
                DialoguePosition.TOP_RIGHT,
                DialoguePosition.BOTTOM_LEFT
            ]
        
        elif dialogue_count == 4:
            # 四个对话：四角分布
            return [
                DialoguePosition.TOP_LEFT,
                DialoguePosition.TOP_RIGHT,
                DialoguePosition.BOTTOM_LEFT,
                DialoguePosition.BOTTOM_RIGHT
            ]
        
        else:
            # 多个对话：交替放置在上下边角
            positions = []
            for i in range(dialogue_count):
                if i % 2 == 0:
                    # 偶数：上方（左右交替）
                    positions.append(DialoguePosition.TOP_LEFT if i % 4 == 0 else DialoguePosition.TOP_RIGHT)
                else:
                    # 奇数：下方（左右交替）
                    positions.append(DialoguePosition.BOTTOM_RIGHT if i % 4 == 1 else DialoguePosition.BOTTOM_LEFT)
            return positions
    
    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        xy: Tuple[int, int, int, int],
        corner_radius: int,
        fill: Tuple[int, int, int, int],
        outline: Tuple[int, int, int, int],
        width: int
    ):
        """绘制圆角矩形"""
        x1, y1, x2, y2 = xy
        
        # 绘制主体矩形
        draw.rectangle([x1 + corner_radius, y1, x2 - corner_radius, y2], fill=fill)
        draw.rectangle([x1, y1 + corner_radius, x2, y2 - corner_radius], fill=fill)
        
        # 绘制四个圆角
        draw.ellipse([x1, y1, x1 + corner_radius * 2, y1 + corner_radius * 2], fill=fill)
        draw.ellipse([x2 - corner_radius * 2, y1, x2, y1 + corner_radius * 2], fill=fill)
        draw.ellipse([x1, y2 - corner_radius * 2, x1 + corner_radius * 2, y2], fill=fill)
        draw.ellipse([x2 - corner_radius * 2, y2 - corner_radius * 2, x2, y2], fill=fill)
        
        # 绘制边框
        if width > 0:
            draw.arc([x1, y1, x1 + corner_radius * 2, y1 + corner_radius * 2], 180, 270, fill=outline, width=width)
            draw.arc([x2 - corner_radius * 2, y1, x2, y1 + corner_radius * 2], 270, 360, fill=outline, width=width)
            draw.arc([x1, y2 - corner_radius * 2, x1 + corner_radius * 2, y2], 90, 180, fill=outline, width=width)
            draw.arc([x2 - corner_radius * 2, y2 - corner_radius * 2, x2, y2], 0, 90, fill=outline, width=width)
            
            draw.line([x1 + corner_radius, y1, x2 - corner_radius, y1], fill=outline, width=width)
            draw.line([x1 + corner_radius, y2, x2 - corner_radius, y2], fill=outline, width=width)
            draw.line([x1, y1 + corner_radius, x1, y2 - corner_radius], fill=outline, width=width)
            draw.line([x2, y1 + corner_radius, x2, y2 - corner_radius], fill=outline, width=width)
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """
        文字自动换行
        
        参数:
            text: 原始文本
            font: 字体对象
            max_width: 最大宽度
        
        返回:
            分行后的文本列表
        """
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text]
    
    def add_dialogue_bubbles(
        self,
        image_base64: str,
        dialogues: List[Dict],
        camera_angle: Optional[str] = None
    ) -> str:
        """
        在图片上添加对话框
        
        参数:
            image_base64: 原始图片的base64编码（data URL格式）
            dialogues: 对话列表
                [
                    {
                        "text": "你好！",
                        "speaker": "角色A",
                        "position": "top_left",  # 可选，不提供则自动分配
                        "bubble_type": "speech"   # 可选，默认为speech
                    }
                ]
            camera_angle: 镜头角度（用于智能定位）
        
        返回:
            添加对话框后的图片base64编码（data URL格式）
        """
        print(f"🎨 开始合成对话框，共 {len(dialogues)} 条对话")
        
        try:
            # 1. 解码base64图片
            if image_base64.startswith('data:image'):
                image_data = image_base64.split(',')[1]
            else:
                image_data = image_base64
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # 转换为RGBA模式（支持透明度）
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # 创建一个透明图层用于绘制对话框
            overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            
            # 2. 自动分配位置（如果没有指定）
            auto_positions = self._auto_position_dialogues(
                image.size, 
                len(dialogues),
                camera_angle
            )
            
            # 3. 逐个绘制对话框
            for i, dialogue in enumerate(dialogues):
                text = dialogue.get("text", "")
                if not text:
                    continue
                
                position = dialogue.get("position") or auto_positions[i]
                bubble_type = dialogue.get("bubble_type", BubbleType.SPEECH)
                speaker = dialogue.get("speaker", "")
                
                # 获取样式配置
                config = self.bubble_config.get(bubble_type, self.bubble_config[BubbleType.SPEECH])
                
                # 字体大小
                font_size = 28
                font = self._get_font(font_size)
                
                # 计算文本尺寸（支持自动换行）
                max_text_width = image.size[0] // 3  # 最大宽度为图片的1/3
                lines = self._wrap_text(text, font, max_text_width)
                
                # 如果有说话人，添加到第一行
                # 修改说明：显示角色名称，格式为"角色名：对话内容"
                # 优化：使用更大、更醒目的字体显示角色名，便于识别说话人
                if speaker and speaker.strip():
                    # 使用比对话内容更大的字体显示角色名
                    speaker_font_size = int(font_size * 1.2)  # 从0.8改为1.2，增大20%
                    speaker_font = self._get_font(speaker_font_size)
                    speaker_line = f"【{speaker}】"  # 使用【】包裹，更醒目
                    lines = [speaker_line] + lines
                
                # 计算对话框尺寸
                line_height = font_size + 10
                text_height = len(lines) * line_height
                text_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])
                
                bubble_width = text_width + config["padding"] * 2
                bubble_height = text_height + config["padding"] * 2
                
                # 计算对话框位置
                bubble_x, bubble_y = self._calculate_bubble_position(
                    image.size,
                    position,
                    (bubble_width, bubble_height)
                )
                
                # 绘制对话框背景
                self._draw_rounded_rectangle(
                    draw,
                    (bubble_x, bubble_y, bubble_x + bubble_width, bubble_y + bubble_height),
                    config["corner_radius"],
                    config["bg_color"],
                    config["border_color"],
                    config["border_width"]
                )
                
                # 绘制文字
                text_x = bubble_x + config["padding"]
                text_y = bubble_y + config["padding"]
                
                # 文字颜色（根据对话框类型）
                # 修改说明：角色名使用深蓝色，专业且醒目
                if bubble_type == BubbleType.CAPTION:
                    text_color = (255, 255, 255, 255)  # 旁白用白色
                    speaker_color = (255, 255, 255, 255)  # 旁白角色名也用白色
                else:
                    text_color = (0, 0, 0, 255)  # 对话内容用黑色
                    speaker_color = (30, 70, 200, 255)  # 角色名用深蓝色，专业醒目
                
                # 修改说明：第一行如果是角色名，使用特殊样式和颜色
                # 优化：角色名使用更大字体、醒目颜色和加粗效果
                for idx, line in enumerate(lines):
                    # 判断是否为角色名行（第一行且包含【】）
                    is_speaker_line = (idx == 0 and speaker and speaker.strip() and '【' in line and '】' in line)
                    
                    if is_speaker_line:
                        # 角色名使用更大的字体和醒目颜色
                        current_font = self._get_font(speaker_font_size)
                        current_color = speaker_color
                        # 加粗效果：绘制3次，让文字更粗更醒目
                        draw.text((text_x, text_y), line, font=current_font, fill=current_color)
                        draw.text((text_x+1, text_y), line, font=current_font, fill=current_color)
                        draw.text((text_x, text_y+1), line, font=current_font, fill=current_color)
                    else:
                        # 普通对话文字
                        draw.text((text_x, text_y), line, font=font, fill=text_color)
                    
                    text_y += line_height
                
                print(f"  ✅ 添加对话框 #{i+1}: '{text[:10]}...' at {position}")
            
            # 4. 合并图层
            final_image = Image.alpha_composite(image, overlay)
            
            # 5. 转换回base64
            output_buffer = io.BytesIO()
            final_image.convert('RGB').save(output_buffer, format='PNG', quality=95)
            output_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
            
            print(f"✅ 对话框合成完成")
            return f"data:image/png;base64,{output_base64}"
            
        except Exception as e:
            print(f"❌ 对话框合成失败: {e}")
            import traceback
            traceback.print_exc()
            # 失败时返回原图
            return image_base64


# 全局实例
comic_composer = ComicComposer()


# 便捷函数
def add_dialogues_to_image(
    image_base64: str,
    dialogues: List[Dict],
    camera_angle: Optional[str] = None
) -> str:
    """
    在图片上添加对话框（便捷函数）
    
    使用示例:
        result = add_dialogues_to_image(
            image_base64="data:image/png;base64,iVBORw0KG...",
            dialogues=[
                {
                    "text": "你好，很高兴见到你！",
                    "speaker": "李慕白",
                    "position": "top_left",  # 可选
                    "bubble_type": "speech"  # 可选
                },
                {
                    "text": "（这个人看起来很厉害）",
                    "bubble_type": "thought",
                    "position": "bottom_right"
                }
            ],
            camera_angle="中景"
        )
    """
    return comic_composer.add_dialogue_bubbles(image_base64, dialogues, camera_angle)

