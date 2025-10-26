"""
添加测试对话数据到数据库

这个脚本会为现有的分镜记录添加测试对话内容
"""
import asyncio
import asyncpg
import json

# 从config.json读取数据库配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

db_config = config['database']


async def add_test_dialogues():
    """为现有分镜添加测试对话"""
    
    # 连接数据库
    conn = await asyncpg.connect(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['database'],
        user=db_config['username'],
        password=db_config['password']
    )
    
    print("✅ 数据库连接成功")
    
    try:
        # 1. 查询现有分镜
        rows = await conn.fetch("""
            SELECT storyboard_id, original_text_snippet, character_appearance
            FROM storyboards
            LIMIT 5
        """)
        
        print(f"\n📊 找到 {len(rows)} 条分镜记录")
        
        if len(rows) == 0:
            print("❌ 数据库中没有分镜数据")
            return
        
        # 2. 为每条分镜添加合适的对话
        test_dialogues = [
            "李慕白：师父，我一定会学有所成的！",
            "这里就是传说中的青莲剑宗吗？",
            "王珂：外面的世界真大啊...",
            "少年心中暗想：这次下山，定要闯出一番名堂。",
            "旁白：就这样，他踏上了未知的旅程。"
        ]
        
        updated_count = 0
        
        for i, row in enumerate(rows):
            storyboard_id = row['storyboard_id']
            snippet = row['original_text_snippet']
            
            # 选择对话内容
            dialogue = test_dialogues[i % len(test_dialogues)]
            
            # 更新记录
            await conn.execute("""
                UPDATE storyboards
                SET dialogue = $1
                WHERE storyboard_id = $2
            """, dialogue, storyboard_id)
            
            updated_count += 1
            print(f"  ✅ 更新分镜 #{i+1}: {storyboard_id}")
            print(f"     原文: {snippet[:30]}...")
            print(f"     对话: {dialogue}")
            print()
        
        print(f"\n🎉 成功更新 {updated_count} 条分镜记录！")
        print("\n现在你可以：")
        print("1. 启动后端: python -m uvicorn app.main:app --reload --port 8000")
        print("2. 打开测试页面: backend/test_comic_composer.html")
        print("3. 点击'加载数据库分镜列表'")
        print("4. 查看对话内容（黄色高亮）")
        print("5. 点击'生成完整漫画（含对话框）'")
        
    finally:
        await conn.close()
        print("\n✅ 数据库连接已关闭")


if __name__ == "__main__":
    print("🚀 开始添加测试对话数据...")
    print()
    asyncio.run(add_test_dialogues())

