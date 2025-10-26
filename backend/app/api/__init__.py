# api包初始化文件
# 这个包包含所有API路由层的接口定义
# 负责处理HTTP请求和响应，调用services层和db层
# 与前端Vue页面直接交互的接口层

# 导出所有API路由模块
from . import auth
from . import storyboard
from . import project
from . import text_to_image
from . import storyboard_image_gen

__all__ = [
    "auth",
    "storyboard", 
    "project",
    "text_to_image",
    "storyboard_image_gen"
]