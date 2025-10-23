"""
Supabase连接测试脚本
用于验证Supabase HTTP API连接是否正常
"""
import asyncio
import sys
import os

# 添加backend目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_database, close_database, db_client, create_user, get_user_by_username


async def test_supabase():
    """测试Supabase连接和基本操作"""
    print("🧪 开始Supabase连接测试...")
    
    # 1. 初始化Supabase连接
    print("\n1️⃣ 初始化Supabase连接...")
    success = await init_database()
    if not success:
        print("❌ Supabase连接初始化失败")
        return False
    
    # 2. 测试连接
    print("\n2️⃣ 测试Supabase连接...")
    is_connected = await db_client.test_connection()
    if not is_connected:
        print("❌ Supabase连接测试失败")
        return False
    print("✅ Supabase连接正常")
    
    # 3. 测试基本查询
    print("\n3️⃣ 测试基本查询...")
    try:
        # 查询用户表
        users = await db_client.select('users')
        print(f"✅ 用户表查询成功，当前用户数量: {len(users)}")
    except Exception as e:
        print(f"❌ 基本查询失败: {e}")
        return False
    
    # 4. 测试创建用户（可选）
    print("\n4️⃣ 测试创建用户...")
    try:
        test_username = "test_user_" + str(int(asyncio.get_event_loop().time()))
        user = await create_user(
            username=test_username,
            email=f"{test_username}@example.com",
            hashed_password="test_password_hash"
        )
        
        if user:
            print(f"✅ 测试用户创建成功: {user.username}")
            
            # 验证用户创建
            retrieved_user = await get_user_by_username(test_username)
            if retrieved_user:
                print(f"✅ 测试用户查询成功: {retrieved_user.username}")
            else:
                print("❌ 测试用户查询失败")
        else:
            print("❌ 测试用户创建失败")
    except Exception as e:
        print(f"❌ 用户操作测试失败: {e}")
    
    # 5. 测试项目操作
    print("\n5️⃣ 测试项目操作...")
    try:
        from app.db import create_project, get_projects_by_user, ProjectVisibility
        
        if user:
            project = await create_project(
                user_id=user.user_id,
                title="测试项目",
                description="这是一个测试项目",
                visibility=ProjectVisibility.PRIVATE
            )
            
            if project:
                print(f"✅ 测试项目创建成功: {project.title}")
                
                # 查询用户项目
                projects = await get_projects_by_user(user.user_id)
                print(f"✅ 用户项目查询成功，项目数量: {len(projects)}")
            else:
                print("❌ 测试项目创建失败")
    except Exception as e:
        print(f"❌ 项目操作测试失败: {e}")
    
    # 6. 关闭连接
    print("\n6️⃣ 关闭Supabase连接...")
    await close_database()
    print("✅ Supabase连接已关闭")
    
    print("\n🎉 Supabase测试完成！")
    return True


if __name__ == "__main__":
    asyncio.run(test_supabase())