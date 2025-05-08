import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import traceback

from app.api import api_router
from app.core.config import settings
from app.core.logging import logger
from app.framework.app_framework import FastAPIFramework


from app.db.mysql_session import mysql
from app.db.mongo import mongodb
from app.db.redis import redis
from app.db.miniodb import async_minio_manager
from app.utils.kafka_producer import kafka_producer_manager
from app.utils.kafka_consumer import kafka_consumer_manager

# 创建 FastAPIFramework 实例
framework = FastAPIFramework(debug_mode=settings.debug_mode)

# 获取 FastAPI 应用实例
app = framework.get_app()

# CORS settings
origins = [
    "*"
]  # ["https://your-frontend-domain.com"],  # 建议生产环境中替换为具体的域名白名单

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件处理代码可以放在这里
    logger.info("FastAPI Starting...")
    try:
        # 按顺序初始化各服务，错误时记录详细日志
        try:
            await mongodb.connect()
            logger.info("MongoDB connected successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            logger.error(traceback.format_exc())
        
        try:
            await kafka_producer_manager.start()
            logger.info("Kafka producer started successfully")
        except Exception as e:
            logger.error(f"Kafka producer failed to start: {str(e)}")
            logger.error(traceback.format_exc())
        
        try:
            await async_minio_manager.init_minio()
            logger.info("MinIO initialized successfully")
        except Exception as e:
            logger.error(f"MinIO initialization failed: {str(e)}")
            logger.error(traceback.format_exc())
            
        # 暂时注释掉Kafka消费者，降低复杂度
        # asyncio.create_task(kafka_consumer_manager.consume_messages())
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(traceback.format_exc())
        # 即使出错，也继续运行，避免整个应用崩溃
        
    logger.info("FastAPI Started")
    yield
    
    # 关闭事件处理代码
    logger.info("FastAPI Shutting down...")
    try:
        await kafka_producer_manager.stop()
        logger.info("Kafka producer stopped")
    except Exception as e:
        logger.error(f"Error stopping Kafka producer: {str(e)}")
    
    try:
        await mysql.close()
        logger.info("MySQL connection closed")
    except Exception as e:
        logger.error(f"Error closing MySQL connection: {str(e)}")
        
    try:
        await mongodb.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")
        
    try:
        await redis.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {str(e)}")
        
    logger.info("FastAPI Closed")


app.router.lifespan_context = lifespan

# 路由
framework.include_router(api_router)

logger.info("FastAPI app configured with settings: %s", settings)
