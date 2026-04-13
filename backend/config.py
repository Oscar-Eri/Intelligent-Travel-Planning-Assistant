"""
旅行地图后端配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 通义千问 API 配置
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_API_KEY: str = "sk-bf9cd3719ec54f4ebd31de97d98fa62d"
    QWEN_MODEL: str = "qwen-plus"
    
    # 高德地图 API 配置（用于地理编码）
    AMAP_API_KEY: str = "242ea7c83bf702a32046bc75c83dbb0d"  # 请填入您的高德地图Web服务Key
    
    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略.env中的额外字段


# 创建全局配置实例
settings = Settings()
