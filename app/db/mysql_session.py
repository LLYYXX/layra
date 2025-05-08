from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import AsyncGenerator
from app.core.logging import logger
import asyncio


class MySQL:
    def __init__(self):
        # 打印数据库连接信息，但隐藏密码
        db_url_parts = settings.db_url.split('@')
        if len(db_url_parts) > 1:
            # 隐藏密码部分
            auth_parts = db_url_parts[0].split(':')
            if len(auth_parts) > 2:
                masked_url = f"{auth_parts[0]}:{auth_parts[1]}:***@{db_url_parts[1]}"
                logger.info(f"Connecting to MySQL with: {masked_url}")
            else:
                logger.warning(f"Database URL format unexpected: unable to mask password")
        
        try:
            logger.info(f"Creating MySQL engine with pool_size={settings.db_pool_size}, max_overflow={settings.db_max_overflow}")
            logger.info(f"Database URL={settings.db_url} (host/db part only)")
            
            self.engine = create_async_engine(
                settings.db_url,
                echo=settings.debug_mode,  # 仅在调试模式下打印SQL语句
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,  # 连接回收时间1小时
                connect_args={"charset": "utf8mb4"}  # 确保使用UTF-8
            )
            self.async_session = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            logger.info("MySQL engine created successfully")
        except Exception as e:
            logger.error(f"Error creating MySQL engine: {str(e)}")
            # 我们允许初始化错误继续，以便应用可以启动
            # 但会在后续使用时报错

    async def initialize(self):
        """尝试连接并验证数据库连接"""
        try:
            # 测试连接
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")
            logger.info("MySQL connection test successful")
            return True
        except Exception as e:
            logger.error(f"MySQL connection test failed: {str(e)}")
            return False

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        try:
            async with self.async_session() as session:
                yield session
        except Exception as e:
            logger.error(f"Error getting MySQL session: {str(e)}")
            # 让调用者知道发生了错误
            raise

    async def close(self):
        try:
            await self.engine.dispose()
            logger.info("MySQL connection closed")
        except Exception as e:
            logger.error(f"Error closing MySQL connection: {str(e)}")


# 创建全局数据库实例
mysql = MySQL()

# 在应用启动时调用initialize方法
async def initialize_db():
    """初始化数据库连接，这应该在应用启动时被调用"""
    success = await mysql.initialize()
    if not success:
        logger.warning("MySQL initialization failed, application may not function correctly")
    return success

async def get_mysql_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in mysql.get_session():
        yield session
