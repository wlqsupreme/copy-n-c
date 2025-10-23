import os
import json
from typing import Optional

class Config:
    """配置管理类，支持多种配置方式"""
    
    def __init__(self):
        self.api_key: Optional[str] = None
        self.model: str = "gpt-oss-120b"
        self.max_tokens: int = 4096
        self.temperature: float = 0.2
        self.timeout: int = 60
        
        # Supabase配置
        self.supabase_url: Optional[str] = None
        self.supabase_anon_key: Optional[str] = None
        self.supabase_service_role_key: Optional[str] = None
        
        # 数据库配置（保留兼容性）
        self.database_url: Optional[str] = None
        self.database_host: Optional[str] = None
        self.database_port: int = 5432
        self.database_name: Optional[str] = None
        self.database_username: Optional[str] = None
        self.database_password: Optional[str] = None
        
        # 按优先级加载配置
        self._load_config()
    
    def _load_config(self):
        """按优先级加载配置：配置文件 > 环境变量 > 默认值"""
        
        # 1. 尝试从配置文件加载
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.api_key = config_data.get('qiniu_api_key')
                    self.model = config_data.get('model', self.model)
                    self.max_tokens = config_data.get('max_tokens', self.max_tokens)
                    self.temperature = config_data.get('temperature', self.temperature)
                    self.timeout = config_data.get('timeout', self.timeout)
                    
                    # 加载Supabase配置
                    supabase_config = config_data.get('supabase', {})
                    self.supabase_url = supabase_config.get('url')
                    self.supabase_anon_key = supabase_config.get('anon_key')
                    self.supabase_service_role_key = supabase_config.get('service_role_key')
                    
                    # 加载数据库配置（保留兼容性）
                    db_config = config_data.get('database', {})
                    self.database_url = db_config.get('url')
                    self.database_host = db_config.get('host')
                    self.database_port = db_config.get('port', self.database_port)
                    self.database_name = db_config.get('database')
                    self.database_username = db_config.get('username')
                    self.database_password = db_config.get('password')
                    
                    print(f"✅ 从配置文件加载成功: {config_file}")
                    return
            except Exception as e:
                print(f"⚠️ 配置文件加载失败: {e}")
        
        # 2. 尝试从环境变量加载
        env_key = os.environ.get("QINIU_API_KEY")
        if env_key:
            self.api_key = env_key
            print("✅ 从环境变量加载成功")
            return
        
        # 3. 检查是否有 .env 文件
        env_file = ".env"
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() == 'QINIU_API_KEY':
                                self.api_key = value.strip().strip('"\'')
                                print("✅ 从 .env 文件加载成功")
                                return
            except Exception as e:
                print(f"⚠️ .env 文件加载失败: {e}")
        
        # 4. 如果都没有，提示用户
        print("❌ 未找到 API Key 配置")
        print("请选择以下任一方式配置：")
        print("1. 创建 config.json 文件（推荐）")
        print("2. 设置环境变量 QINIU_API_KEY")
        print("3. 创建 .env 文件")
    
    def is_valid(self) -> bool:
        """检查配置是否有效"""
        return self.api_key is not None and len(self.api_key.strip()) > 0
    
    def is_database_configured(self) -> bool:
        """检查Supabase配置是否完整"""
        return (
            self.supabase_url is not None and len(self.supabase_url.strip()) > 0 and
            self.supabase_service_role_key is not None and len(self.supabase_service_role_key.strip()) > 0
        )
    
    def get_error_message(self) -> str:
        """获取配置错误信息"""
        if not self.api_key:
            return """
请配置七牛云 API Key，选择以下任一方式：

方式1（推荐）：创建 config.json 文件
{
  "qiniu_api_key": "你的七牛API密钥",
  "model": "gpt-oss-120b",
  "max_tokens": 4096,
  "temperature": 0.2,
  "database": {
    "url": "postgresql://postgres:[YOUR_PASSWORD]@db.ihpmirffjziqvkkaplpl.supabase.co:5432/postgres",
    "host": "db.ihpmirffjziqvkkaplpl.supabase.co",
    "port": 5432,
    "database": "postgres",
    "username": "postgres",
    "password": "你的数据库密码"
  }
}

方式2：设置环境变量
export QINIU_API_KEY="你的七牛API密钥"

方式3：创建 .env 文件
QINIU_API_KEY=你的七牛API密钥
"""
        return ""

# 全局配置实例
config = Config()
