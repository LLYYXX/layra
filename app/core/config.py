from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    api_version_url: str = "/api/v1"
    max_workers: int = 10
    log_level: str = "INFO"
    log_file: str = os.path.join("logs", "layra.log")
    
    # 数据库设置 - 默认值适用于本地开发，Docker环境通过环境变量覆盖
    db_url: str = "mysql+asyncmy://mysqluser:password@mysql/imagedb"  # Docker环境中使用容器名称
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Redis设置
    redis_url: str = "redis:6379"  # Docker环境中使用容器名称
    redis_password: str = "password"
    redis_token_db: int = 0  # 用于token存储
    redis_task_db: int = 1  # 用于存储embedding任务队列
    redis_lock_db: int = 2  # 用于存储embedding任务队列
    
    # JWT设置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 36000  # 约25天
    
    # MongoDB设置
    mongodb_url: str = "mongodb:27017"  # Docker环境中使用容器名称
    mongodb_db: str = "mongodb"
    mongodb_root_username: str = "mongouser"
    mongodb_root_password: str = "mongo577715"
    mongodb_pool_size: int = 100  # MongoDB 最大连接池大小
    mongodb_min_pool_size: int = 10  # MongoDB 最小连接池大小
    
    # 调试设置
    debug_mode: bool = True
    
    # Kafka设置
    kafka_broker_url: str = "kafka:9092"  # Docker环境中使用容器名称
    kafka_topic: str = "task_generation"
    kafka_group_id: str = "task_consumer_group"
    
    # MinIO设置
    minio_url: str = "http://minio:9110"  # Docker环境中使用容器名称
    minio_access_key: str = "minioadmin"  # MinIO 的访问密钥
    minio_secret_key: str = "minioadmin"  # MinIO 的密钥
    minio_bucket_name: str = "ai-chat"  # 需要上传的桶的名称
    
    # Milvus设置
    milvus_uri: str = "http://milvus:19530"  # Docker环境中使用容器名称
    
    # 模型设置
    colbert_model_path: str = "/path/to/model"
    
    # MySQL密码
    mysql_root_password: str = "password"
    mysql_password: str = "password"
    mysql_port: int = 3306
    
    # 新增API服务配置
    use_api_embedding: bool = True  # 是否使用API嵌入服务
    embedding_api_url: str = "https://openrouter.ai/api/v1"  # OpenRouter API URL
    embedding_api_key: str = ""  # OpenRouter API密钥
    embedding_model_name: str = ""  # 文本嵌入模型名称
    image_embedding_model_name: str = ""  # 图像嵌入模型名称
    site_url: Optional[str] = None  # 在OpenRouter上显示的网站URL，可选
    site_name: Optional[str] = None  # 在OpenRouter上显示的网站名称，可选

    class Config:
        env_file = ".env"
        env_prefix = ""  # 移除APP_前缀
        extra = "ignore"  # 忽略未在模型中定义的额外环境变量


settings = Settings()
# print(settings.mongodb_url)  # 这里应只打印 "localhost:27017"
