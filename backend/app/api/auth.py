"""
认证API路由
处理用户登录、注册、令牌验证等HTTP请求
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import os
import sys

# 添加 backend 目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入认证服务和数据库层
from app.services.auth_service import auth_service
from app.db import db_client
from app.db.models import User

# 创建认证相关的路由器
router = APIRouter()

# HTTP Bearer认证
security = HTTPBearer()


# ==================== 请求模型 ====================

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str
    email: str
    password: str


class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    """用户信息响应模型"""
    user_id: str
    username: str
    email: str
    credit_balance: int


# ==================== 依赖函数 ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    获取当前用户依赖函数
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ==================== API接口 ====================

@router.post("/api/v1/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(request: LoginRequest):
    """
    用户登录接口
    
    功能说明：
    - 验证用户名/邮箱和密码
    - 生成JWT访问令牌
    - 返回用户信息和令牌
    
    使用场景：
    - 用户登录系统
    - 获取访问权限
    
    参数：
        username: 用户名或邮箱
        password: 密码
    
    返回：
        TokenResponse: 包含访问令牌和用户信息
    """
    print(f"🔐(API) 收到登录请求:")
    print(f"   用户名/邮箱: {request.username}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 验证用户身份
        user = await auth_service.authenticate_user(request.username, request.password)
        
        if not user:
            print(f"❌(API) 登录失败: 用户名或密码错误")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 创建访问令牌
        token_data = auth_service.create_user_token(user)
        
        print(f"✅(API) 用户登录成功: {user.username}")
        return TokenResponse(**token_data)
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"❌(API) 登录失败: {e}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@router.post("/api/v1/auth/register", response_model=TokenResponse, tags=["Auth"])
async def register(request: RegisterRequest):
    """
    用户注册接口
    
    功能说明：
    - 创建新用户账户
    - 验证用户名和邮箱唯一性
    - 自动生成JWT访问令牌
    
    使用场景：
    - 新用户注册
    - 创建账户
    
    参数：
        username: 用户名
        email: 邮箱地址
        password: 密码
    
    返回：
        TokenResponse: 包含访问令牌和用户信息
    """
    print(f"📝(API) 收到注册请求:")
    print(f"   用户名: {request.username}")
    print(f"   邮箱: {request.email}")
    
    # 检查数据库连接状态
    if not db_client.is_connected:
        raise HTTPException(status_code=500, detail="数据库未连接")
    
    try:
        # 验证输入数据
        if len(request.username) < 3:
            raise HTTPException(status_code=400, detail="用户名至少需要3个字符")
        
        if len(request.password) < 6:
            raise HTTPException(status_code=400, detail="密码至少需要6个字符")
        
        # 注册新用户
        user = await auth_service.register_user(
            request.username,
            request.email,
            request.password
        )
        
        if not user:
            raise HTTPException(status_code=500, detail="用户注册失败")
        
        # 创建访问令牌
        token_data = auth_service.create_user_token(user)
        
        print(f"✅(API) 用户注册成功: {user.username}")
        return TokenResponse(**token_data)
        
    except ValueError as e:
        # 业务逻辑错误（如用户名已存在）
        print(f"❌(API) 注册失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"❌(API) 注册失败: {e}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.get("/api/v1/auth/me", response_model=UserResponse, tags=["Auth"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息接口
    
    功能说明：
    - 根据JWT令牌获取当前用户信息
    - 验证令牌有效性
    - 返回用户基本信息
    
    使用场景：
    - 获取当前登录用户信息
    - 验证用户身份
    
    返回：
        UserResponse: 用户信息
    """
    print(f"👤(API) 获取用户信息: {current_user.username}")
    
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        credit_balance=current_user.credit_balance
    )


@router.post("/api/v1/auth/refresh", response_model=TokenResponse, tags=["Auth"])
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    刷新访问令牌接口
    
    功能说明：
    - 为当前用户生成新的访问令牌
    - 延长用户会话时间
    - 返回新的令牌信息
    
    使用场景：
    - 令牌即将过期时刷新
    - 延长用户会话
    
    返回：
        TokenResponse: 新的访问令牌和用户信息
    """
    print(f"🔄(API) 刷新令牌: {current_user.username}")
    
    try:
        # 创建新的访问令牌
        token_data = auth_service.create_user_token(current_user)
        
        print(f"✅(API) 令牌刷新成功: {current_user.username}")
        return TokenResponse(**token_data)
        
    except Exception as e:
        print(f"❌(API) 令牌刷新失败: {e}")
        raise HTTPException(status_code=500, detail=f"令牌刷新失败: {str(e)}")


@router.post("/api/v1/auth/logout", tags=["Auth"])
async def logout():
    """
    用户登出接口
    
    功能说明：
    - 客户端登出（服务端无状态，主要靠客户端删除令牌）
    - 返回登出成功信息
    
    使用场景：
    - 用户主动登出
    - 清理客户端状态
    
    返回：
        dict: 登出成功信息
    """
    print(f"🚪(API) 用户登出")
    
    return {
        "message": "登出成功",
        "ok": True
    }


# ==================== 健康检查接口 ====================

@router.get("/api/v1/auth/health", tags=["Auth"])
async def auth_health():
    """
    认证服务健康检查接口
    
    功能说明：
    - 检查认证服务是否正常运行
    - 验证数据库连接状态
    
    返回：
        dict: 服务状态信息
    """
    try:
        # 检查数据库连接
        is_db_connected = db_client.is_connected
        
        return {
            "status": "ok",
            "message": "认证服务正常运行",
            "database_connected": is_db_connected,
            "timestamp": str(datetime.now())
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"认证服务异常: {str(e)}",
            "database_connected": False,
            "timestamp": str(datetime.now())
        }


