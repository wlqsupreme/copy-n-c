#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中 panel_elements 字段的数据

这个脚本会：
1. 连接数据库
2. 查询所有分镜的 panel_elements 字段
3. 显示哪些分镜有对话数据
4. 显示对话内容和关联的角色ID
"""

import asyncio
import asyncpg
from config import config
import json

async def check_panel_elements():
    """检查 panel_elements 字段"""
    
    print("=" * 80)
    print("📊 开始检查 panel_elements 字段")
    print("=" * 80)
    
    # 连接数据库
    try:
        conn = await asyncpg.connect(
            host=config.database_host,
            port=config.database_port or 5432,
            database=config.database_name,
            user=config.database_username,
            password=config.database_password
        )
        print("✅ 数据库连接成功\n")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    try:
        # 查询所有分镜的 panel_elements
        query = """
            SELECT 
                storyboard_id,
                original_text_snippet,
                panel_elements,
                created_at
            FROM storyboards
            ORDER BY created_at DESC
            LIMIT 50
        """
        
        rows = await conn.fetch(query)
        
        print(f"📚 查询到 {len(rows)} 条分镜数据\n")
        print("=" * 80)
        
        has_dialogue_count = 0
        empty_count = 0
        
        for idx, row in enumerate(rows, 1):
            storyboard_id = row['storyboard_id']
            text_snippet = row['original_text_snippet'] or "无"
            panel_elements = row['panel_elements']
            
            print(f"\n📍 分镜 #{idx}")
            print(f"   ID: {storyboard_id}")
            print(f"   原文片段: {text_snippet[:50]}...")
            
            # 检查 panel_elements
            if panel_elements:
                # 解析 JSON
                try:
                    if isinstance(panel_elements, str):
                        elements = json.loads(panel_elements)
                    else:
                        elements = panel_elements
                    
                    if isinstance(elements, list) and len(elements) > 0:
                        # 筛选有 dialogue 字段的元素
                        dialogues = [e for e in elements if e.get('dialogue')]
                        
                        if dialogues:
                            has_dialogue_count += 1
                            print(f"   ✅ 包含 {len(dialogues)} 条对话:")
                            
                            for d_idx, dialogue_item in enumerate(dialogues, 1):
                                dialogue_text = dialogue_item.get('dialogue', '')
                                character_id = dialogue_item.get('characterid', '无')
                                
                                print(f"      💬 对话 {d_idx}:")
                                print(f"         内容: {dialogue_text[:50]}{'...' if len(dialogue_text) > 50 else ''}")
                                print(f"         角色ID: {character_id}")
                                
                                # 尝试查询角色名称
                                if character_id and character_id != '无':
                                    try:
                                        char_query = "SELECT name FROM characters WHERE character_id = $1"
                                        char_row = await conn.fetchrow(char_query, character_id)
                                        if char_row:
                                            print(f"         角色名: {char_row['name']}")
                                        else:
                                            print(f"         ⚠️ 角色ID不存在于 characters 表")
                                    except Exception as e:
                                        print(f"         ❌ 查询角色失败: {e}")
                        else:
                            empty_count += 1
                            print(f"   ⚪ panel_elements 存在但无对话内容")
                    else:
                        empty_count += 1
                        print(f"   ⚪ panel_elements 为空数组")
                        
                except Exception as e:
                    print(f"   ❌ 解析 panel_elements 失败: {e}")
                    empty_count += 1
            else:
                empty_count += 1
                print(f"   ⚪ panel_elements 字段为空 (NULL)")
            
            print("-" * 80)
        
        print("\n" + "=" * 80)
        print("📊 统计结果:")
        print(f"   总分镜数: {len(rows)}")
        print(f"   ✅ 有对话内容: {has_dialogue_count} 条")
        print(f"   ⚪ 无对话内容: {empty_count} 条")
        print("=" * 80)
        
        # 查询 characters 表统计
        char_count_query = "SELECT COUNT(*) FROM characters"
        char_count = await conn.fetchval(char_count_query)
        print(f"\n👥 characters 表共有 {char_count} 个角色")
        
        if char_count > 0:
            print("\n前10个角色:")
            char_query = "SELECT character_id, name FROM characters LIMIT 10"
            char_rows = await conn.fetch(char_query)
            for char in char_rows:
                print(f"   - {char['name']} (ID: {char['character_id']})")
        
        print("\n" + "=" * 80)
        
    finally:
        await conn.close()
        print("\n✅ 数据库连接已关闭")


if __name__ == "__main__":
    asyncio.run(check_panel_elements())

