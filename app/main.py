import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
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
    "http://localhost:3000",      # 本地前端开发服务器
    "http://127.0.0.1:3000",      # 本地前端开发服务器（IP形式）
    "http://frontend:3000",       # Docker Compose中的前端服务
    "http://localhost:8000",      # 本地后端服务器
    "http://127.0.0.1:8000",      # 本地后端服务器（IP形式）
    "http://backend:8000",        # Docker Compose中的后端服务
]  # 建议生产环境中替换为具体的域名白名单

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器，捕获所有未处理的异常
    记录详细错误日志，但只向客户端返回简洁的错误信息
    """
    # 记录详细错误信息到日志
    error_detail = f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}"
    logger.error(error_detail)
    
    # 向客户端返回简洁的错误信息
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请联系我❤"},
    )

# 处理验证错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证错误，提供友好的中文错误信息
    """
    # 记录到日志
    logger.warning(f"Request validation error: {exc.errors()}")
    
    # 格式化错误信息
    error_messages = []
    for error in exc.errors():
        field = error.get("loc", ["未知字段"])[-1]
        msg = error.get("msg", "验证错误")
        error_messages.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": error_messages},
    )

# 处理HTTP异常
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    处理HTTP异常，包括401、403、404等
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件处理代码可以放在这里
    logger.info("FastAPI Starting...")
    try:
        # 按顺序初始化各服务，错误时记录详细日志
        # 验证MySQL连接
        try:
            from app.db.mysql_session import initialize_db
            mysql_ok = await initialize_db()
            if not mysql_ok:
                logger.warning("MySQL初始化失败，应用可能无法正常工作")
            else:
                logger.info("MySQL初始化成功")
        except Exception as e:
            logger.error(f"MySQL初始化异常: {str(e)}")
            logger.error(traceback.format_exc())
        
        # 连接MongoDB
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
