"""
认证服务层
负责用户认证相关的业务逻辑
包括密码加密、JWT生成和验证、用户认证等
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from ..db.models import User
from ..db.crud import get_user_by_username, get_user_by_email, create_user


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 加密后的密码
            
        Returns:
            bool: 密码是否正确
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        生成密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            str: 加密后的密码
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT令牌
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Optional[Dict[str, Any]]: 解码后的数据或None
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def authenticate_user(username_or_email: str, password: str) -> Optional[User]:
        """
        验证用户身份
        
        Args:
            username_or_email: 用户名或邮箱
            password: 密码
            
        Returns:
            Optional[User]: 验证成功的用户对象或None
        """
        # 判断输入是用户名还是邮箱
        if "@" in username_or_email:
            user = await get_user_by_email(username_or_email)
        else:
            user = await get_user_by_username(username_or_email)
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    async def register_user(username: str, email: str, password: str) -> Optional[User]:
        """
        注册新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            Optional[User]: 创建的用户对象或None
        """
        # 检查用户名是否已存在
        existing_user = await get_user_by_username(username)
        if existing_user:
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        existing_email = await get_user_by_email(email)
        if existing_email:
            raise ValueError("邮箱已被注册")
        
        # 加密密码
        hashed_password = AuthService.get_password_hash(password)
        
        # 创建用户
        user = await create_user(username, email, hashed_password)
        return user
    
    @staticmethod
    def create_user_token(user: User) -> Dict[str, Any]:
        """
        为用户创建访问令牌
        
        Args:
            user: 用户对象
            
        Returns:
            Dict[str, Any]: 包含令牌信息的字典
        """
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.user_id, "username": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "credit_balance": user.credit_balance
            }
        }
    
    @staticmethod
    async def get_current_user(token: str) -> Optional[User]:
        """
        根据令牌获取当前用户
        
        Args:
            token: JWT令牌
            
        Returns:
            Optional[User]: 用户对象或None
        """
        payload = AuthService.verify_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        # 这里需要导入get_user_by_id函数
        from ..db.crud import get_user_by_id
        user = await get_user_by_id(user_id)
        return user


# 创建全局认证服务实例
auth_service = AuthService()


