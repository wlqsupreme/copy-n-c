#!/usr/bin/env python3
"""
认证功能测试脚本
测试用户注册、登录和令牌验证功能
"""
import asyncio
import sys
import os

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.auth_service import auth_service
from app.db.crud import create_user, get_user_by_username, get_user_by_email
from app.db import init_database, close_database


async def test_auth_functions():
    """测试认证相关功能"""
    print("🧪 开始测试认证功能...")
    
    # 初始化数据库连接
    print("🔗 初始化数据库连接...")
    db_success = await init_database()
    if not db_success:
        print("❌ 数据库连接初始化失败")
        return
    
    # 测试数据
    test_username = "test_user_123"
    test_email = "test@example.com"
    test_password = "test123"  # 缩短密码长度
    
    try:
        # 1. 测试密码加密
        print("\n1️⃣ 测试密码加密...")
        hashed_password = auth_service.get_password_hash(test_password)
        print(f"   原始密码: {test_password}")
        print(f"   加密后密码: {hashed_password[:50]}...")
        
        # 2. 测试密码验证
        print("\n2️⃣ 测试密码验证...")
        is_valid = auth_service.verify_password(test_password, hashed_password)
        print(f"   密码验证结果: {is_valid}")
        
        # 3. 测试JWT令牌生成
        print("\n3️⃣ 测试JWT令牌生成...")
        test_data = {"sub": "test_user_id", "username": test_username}
        token = auth_service.create_access_token(test_data)
        print(f"   生成的令牌: {token[:50]}...")
        
        # 4. 测试JWT令牌验证
        print("\n4️⃣ 测试JWT令牌验证...")
        payload = auth_service.verify_token(token)
        print(f"   令牌验证结果: {payload}")
        
        # 5. 测试用户注册（模拟）
        print("\n5️⃣ 测试用户注册...")
        try:
            # 这里只是测试业务逻辑，不实际创建数据库记录
            print("   检查用户名是否已存在...")
            existing_user = await get_user_by_username(test_username)
            if existing_user:
                print(f"   用户名 {test_username} 已存在")
            else:
                print(f"   用户名 {test_username} 可用")
            
            print("   检查邮箱是否已存在...")
            existing_email = await get_user_by_email(test_email)
            if existing_email:
                print(f"   邮箱 {test_email} 已被注册")
            else:
                print(f"   邮箱 {test_email} 可用")
                
        except Exception as e:
            print(f"   数据库操作测试失败: {e}")
        
        print("\n✅ 认证功能测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await close_database()


async def test_user_creation():
    """测试用户创建功能"""
    print("\n🧪 开始测试用户创建功能...")
    
    # 初始化数据库连接
    print("🔗 初始化数据库连接...")
    db_success = await init_database()
    if not db_success:
        print("❌ 数据库连接初始化失败")
        return
    
    test_username = "test_user_create"
    test_email = "test_create@example.com"
    test_password = "test123"  # 缩短密码长度
    
    try:
        # 加密密码
        hashed_password = auth_service.get_password_hash(test_password)
        
        # 创建用户
        print(f"   创建用户: {test_username}")
        user = await create_user(test_username, test_email, hashed_password)
        
        if user:
            print(f"   ✅ 用户创建成功: {user.username}")
            print(f"   用户ID: {user.user_id}")
            print(f"   邮箱: {user.email}")
            print(f"   积分余额: {user.credit_balance}")
        else:
            print("   ❌ 用户创建失败")
            
    except Exception as e:
        print(f"   ❌ 用户创建测试失败: {e}")
    finally:
        # 关闭数据库连接
        await close_database()


if __name__ == "__main__":
    print("🚀 启动认证功能测试")
    
    # 运行测试
    asyncio.run(test_auth_functions())
    asyncio.run(test_user_creation())
    
    print("\n🎉 所有测试完成！")


