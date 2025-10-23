import asyncio
import asyncpg
from config import config

class DatabaseManager:
    """数据库连接管理器"""
    
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """建立数据库连接池"""
        if not config.is_database_configured():
            print("⚠️ 数据库未配置，跳过数据库连接")
            return False
        
        try:
            if config.database_url:
                # 使用完整的数据库URL
                self.pool = await asyncpg.create_pool(
                    config.database_url,
                    min_size=1,
                    max_size=10
                )
            else:
                # 使用单独的连接参数
                self.pool = await asyncpg.create_pool(
                    host=config.database_host,
                    port=config.database_port,
                    database=config.database_name,
                    user=config.database_username,
                    password=config.database_password,
                    min_size=1,
                    max_size=10
                )
            
            print("✅ 数据库连接池创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            await self.pool.close()
            print("✅ 数据库连接池已关闭")
    
    async def execute(self, query: str, *args):
        """执行SQL查询"""
        if not self.pool:
            raise Exception("数据库未连接")
        
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """获取查询结果"""
        if not self.pool:
            raise Exception("数据库未连接")
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """获取单行查询结果"""
        if not self.pool:
            raise Exception("数据库未连接")
        
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def init_tables(self):
        """初始化数据库表"""
        if not self.pool:
            return False
        
        try:
            # 创建用户表
            await self.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建项目表
            await self.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    storyboard_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建分镜表
            await self.execute("""
                CREATE TABLE IF NOT EXISTS storyboards (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES projects(id),
                    page_index INTEGER NOT NULL,
                    panels_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            print("✅ 数据库表初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 数据库表初始化失败: {e}")
            return False

# 全局数据库管理器实例
db_manager = DatabaseManager()
