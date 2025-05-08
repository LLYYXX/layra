from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    api_version_url: str = "/api/v1"
    max_workers: int = 10
    log_level: str = "INFO"
    log_file: str = "layra.log"
    db_url: str = "mysql+asyncmy://mysqluser:password@localhost/imagedb"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    redis_url: str = "localhost:6379"
    redis_password: str = "password"
    redis_token_db: int = 0  # 用于token存储
    redis_task_db: int = 1  # 用于存储embedding任务队列
    redis_lock_db: int = 2  # 用于存储embedding任务队列
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 36000  # 约25天
    mongodb_url: str = "localhost:27017"
    mongodb_db: str = "mongodb"
    mongodb_root_username: str = "mongouser"
    mongodb_root_password: str = "password"
    mongodb_pool_size: int = 100  # MongoDB 最大连接池大小
    mongodb_min_pool_size: int = 10  # MongoDB 最小连接池大小
    debug_mode: bool = True
    kafka_broker_url: str = "localhost:9094"
    kafka_topic: str = "task_generation"
    kafka_group_id: str = "task_consumer_group"
    # kafka_priority_levels: int = 5  # 定义优先级的级别（0为最高）
    minio_url: str = "http://127.0.0.1:9110"  # MinIO 服务的URL
    minio_access_key: str = "miniouser"  # MinIO 的访问密钥
    minio_secret_key: str = "password"  # MinIO 的密钥
    minio_bucket_name: str = "ai-chat"  # 需要上传的桶的名称
    milvus_uri: str = "http://127.0.0.1:19530"
    colbert_model_path: str = "/path/to/model"
    
    # 新增API服务配置
    use_api_embedding: bool = True  # 是否使用API嵌入服务
    embedding_api_url: str = "https://openrouter.ai/api/v1"  # OpenRouter API URL
    embedding_api_key: str = ""  # OpenRouter API密钥
    embedding_model_name: str = "openai/text-embedding-3-large"  # 文本嵌入模型名称
    image_embedding_model_name: str = "openai/gpt-4o"  # 图像嵌入模型名称，使用GPT-4o处理图像
    site_url: Optional[str] = None  # 在OpenRouter上显示的网站URL，可选
    site_name: Optional[str] = None  # 在OpenRouter上显示的网站名称，可选

    class Config:
        env_file = ".env"
        env_prefix = ""  # 移除APP_前缀


settings = Settings()
# print(settings.mongodb_url)  # 这里应只打印 "localhost:27017"
