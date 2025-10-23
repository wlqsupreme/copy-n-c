"""
Supabase数据库客户端管理
使用Supabase SDK进行HTTP API连接
"""
import asyncio
from typing import Optional, List, Dict, Any
import sys
import os

# 添加父目录到路径，以便导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ 请安装Supabase SDK: pip install supabase")
    sys.exit(1)


class SupabaseClient:
    """Supabase数据库客户端"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """
        建立Supabase连接
        
        Returns:
            bool: 连接是否成功
        """
        if not config.is_database_configured():
            print("⚠️ Supabase未配置，跳过连接")
            return False
        
        try:
            # 创建Supabase客户端
            self.client = create_client(
                config.supabase_url,
                config.supabase_service_role_key  # 使用service_role_key进行服务端操作
            )
            
            self._connected = True
            print("✅ Supabase客户端创建成功")
            return True
            
        except Exception as e:
            print(f"❌ Supabase连接失败: {e}")
            self._connected = False
            return False
    
    async def close(self):
        """关闭Supabase连接"""
        if self.client:
            # Supabase客户端不需要显式关闭
            self._connected = False
            print("✅ Supabase客户端已关闭")
    
    async def test_connection(self) -> bool:
        """
        测试Supabase连接
        
        Returns:
            bool: 连接是否正常
        """
        try:
            if not self._connected or not self.client:
                return False
            
            # 尝试查询用户表来测试连接
            result = self.client.table('users').select('*').limit(1).execute()
            return True
            
        except Exception as e:
            print(f"❌ Supabase连接测试失败: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected and self.client is not None
    
    # 便捷方法，封装Supabase操作
    async def select(self, table: str, columns: str = "*", filters: Optional[Dict] = None) -> List[Dict]:
        """
        查询数据
        
        Args:
            table: 表名
            columns: 查询列
            filters: 过滤条件
            
        Returns:
            List[Dict]: 查询结果
        """
        if not self._connected or not self.client:
            raise Exception("Supabase未连接")
        
        try:
            query = self.client.table(table).select(columns)
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            raise
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        插入数据
        
        Args:
            table: 表名
            data: 插入数据
            
        Returns:
            Dict[str, Any]: 插入结果
        """
        if not self._connected or not self.client:
            raise Exception("Supabase未连接")
        
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            print(f"❌ 插入失败: {e}")
            raise
    
    async def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        更新数据
        
        Args:
            table: 表名
            data: 更新数据
            filters: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 更新结果
        """
        if not self._connected or not self.client:
            raise Exception("Supabase未连接")
        
        try:
            query = self.client.table(table).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            print(f"❌ 更新失败: {e}")
            raise
    
    async def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        删除数据
        
        Args:
            table: 表名
            filters: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 删除结果
        """
        if not self._connected or not self.client:
            raise Exception("Supabase未连接")
        
        try:
            query = self.client.table(table).delete()
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            raise
    
    async def upsert(self, table: str, data: List[Dict[str, Any]], on_conflict: str = None) -> List[Dict[str, Any]]:
        """
        插入或更新数据
        
        Args:
            table: 表名
            data: 数据列表
            on_conflict: 冲突处理列
            
        Returns:
            List[Dict[str, Any]]: 操作结果
        """
        if not self._connected or not self.client:
            raise Exception("Supabase未连接")
        
        try:
            query = self.client.table(table).upsert(data)
            
            if on_conflict:
                query = query.on_conflict(on_conflict)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            print(f"❌ 插入或更新失败: {e}")
            raise


# 全局Supabase客户端实例
db_client = SupabaseClient()


async def init_database():
    """初始化Supabase连接"""
    return await db_client.connect()


async def close_database():
    """关闭Supabase连接"""
    await db_client.close()


# 便捷函数
async def select_data(table: str, columns: str = "*", filters: Optional[Dict] = None) -> List[Dict]:
    """查询数据"""
    return await db_client.select(table, columns, filters)


async def insert_data(table: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """插入数据"""
    return await db_client.insert(table, data)


async def update_data(table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """更新数据"""
    return await db_client.update(table, data, filters)


async def delete_data(table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """删除数据"""
    return await db_client.delete(table, filters)


async def upsert_data(table: str, data: List[Dict[str, Any]], on_conflict: str = None) -> List[Dict[str, Any]]:
    """插入或更新数据"""
    return await db_client.upsert(table, data, on_conflict)