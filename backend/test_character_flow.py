#!/usr/bin/env python3
"""
测试角色数据流的正确性
验证"项目感知"的AI处理流程
"""

import asyncio
import sys
import os

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import init_database, close_database, db_client
from app.services.ai_parser import generate_storyboard_for_segment


async def test_character_flow():
    """测试角色数据流"""
    print("🧪 开始测试角色数据流...")
    
    # 1. 初始化数据库
    await init_database()
    if not db_client.is_connected:
        print("❌ 数据库连接失败")
        return
    
    print("✅ 数据库连接成功")
    
    # 2. 测试场景1：首次上传（没有已存在角色）
    print("\n📖 测试场景1：首次上传（没有已存在角色）")
    existing_chars_1 = []  # 空列表，模拟首次上传
    
    result_1 = await generate_storyboard_for_segment(
        segment_text="李慕白背着行囊，最后看了一眼山顶的茅屋，毅然转身下山。",
        title="第一章：下山",
        segment_index=1,
        existing_characters=existing_chars_1
    )
    
    print(f"   结果：识别到 {len(result_1.get('characters', []))} 个新角色")
    print(f"   结果：生成 {len(result_1.get('storyboards', []))} 个分镜")
    
    # 3. 测试场景2：后续上传（有已存在角色）
    print("\n📖 测试场景2：后续上传（有已存在角色）")
    existing_chars_2 = [
        {"name": "李慕白", "description": "年龄17岁, 男性, 身高178cm, 身材修长, 黑色长发束成马尾, 黑色眼眸犀利, 穿着朴素的蓝色武道袍, 背着一个竹制背包和一把剑"},
        {"name": "王珂", "description": "年龄22岁, 女性, 身高165cm, 中等身材, 凌乱的黑色短发, 惊恐的大眼睛, 穿着宽大的T恤和短裤, 没有配饰"}
    ]
    
    result_2 = await generate_storyboard_for_segment(
        segment_text="王珂缩在角落，借着闪电的光芒，她看到那个黑影又一次出现在了巷口。",
        title="第二章：雨夜",
        segment_index=2,
        existing_characters=existing_chars_2
    )
    
    print(f"   结果：识别到 {len(result_2.get('characters', []))} 个新角色")
    print(f"   结果：生成 {len(result_2.get('storyboards', []))} 个分镜")
    
    # 4. 验证结果
    print("\n🔍 验证结果：")
    
    # 场景1应该识别到新角色
    if result_1.get('characters'):
        print("✅ 场景1：正确识别到新角色（李慕白）")
        for char in result_1['characters']:
            print(f"   - 角色: {char.get('name')}")
    else:
        print("❌ 场景1：应该识别到新角色，但没有")
    
    # 场景2应该不识别已存在的角色
    if not result_2.get('characters'):
        print("✅ 场景2：正确跳过已存在角色，没有重复创建")
    else:
        print("❌ 场景2：不应该识别已存在的角色")
        for char in result_2['characters']:
            print(f"   - 意外角色: {char.get('name')}")
    
    # 两个场景都应该生成分镜
    if result_1.get('storyboards') and result_2.get('storyboards'):
        print("✅ 两个场景都正确生成了分镜")
    else:
        print("❌ 分镜生成失败")
    
    print("\n🎉 角色数据流测试完成！")


if __name__ == "__main__":
    asyncio.run(test_character_flow())
