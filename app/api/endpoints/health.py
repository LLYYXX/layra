from fastapi import APIRouter, Depends
from app.db.mysql_session import mysql
from app.db.mongo import mongodb
from app.db.redis import redis
from app.db.milvus import milvus_client
from app.utils.embedding_check import check_embedding_services
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=dict)
async def health_check():
    """
    系统健康检查接口
    """
    # 检查数据库连接
    db_status = {
        "mysql": await check_mysql(),
        "mongodb": await check_mongodb(),
        "redis": await check_redis(),
        "milvus": check_milvus(),
    }
    
    # 检查嵌入服务
    embedding_service = await check_embedding_services()
    
    return {
        "status": "healthy" if all(s["status"] == "connected" for s in db_status.values()) and embedding_service["status"] == "success" else "unhealthy",
        "database": db_status,
        "embedding_service": embedding_service,
        "app_mode": "api" if settings.use_api_embedding else "local"
    }


async def check_mysql():
    """检查MySQL连接状态"""
    try:
        # 尝试执行简单查询
        async with mysql.engine.begin() as conn:
            await conn.execute("SELECT 1")
        return {"status": "connected"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}


async def check_mongodb():
    """检查MongoDB连接状态"""
    try:
        # 尝试执行简单查询
        await mongodb.db.command("ping")
        return {"status": "connected"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}


async def check_redis():
    """检查Redis连接状态"""
    try:
        # 尝试执行简单命令
        await redis.ping()
        return {"status": "connected"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}


def check_milvus():
    """检查Milvus连接状态"""
    try:
        # 尝试获取所有集合
        collections = milvus_client.list_collections()
        return {"status": "connected", "collections": len(collections)}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)} 