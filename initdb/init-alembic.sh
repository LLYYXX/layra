#!/bin/bash

# 等待MySQL准备就绪
echo "Waiting for MySQL to be ready..."
until mysqladmin ping -h mysql -u mysqluser -pmysql577715 --silent; do
  echo "MySQL not ready yet, waiting..."
  sleep 3
done
echo "MySQL is ready!"

# 设置工作目录
cd /app

# 安装必要的依赖
pip install alembic sqlalchemy

# 如果migrations目录不存在则初始化alembic
if [ ! -d migrations ]; then
  echo "Initializing alembic migrations..."
  alembic init migrations
  cp env.py migrations/
fi

# 检查是否已经有迁移版本存在
if [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
  echo "Creating initial migration..."
  alembic revision --autogenerate -m "Init MySQL"
fi

# 执行数据库迁移
echo "Running database migrations..."
alembic upgrade head

echo "Database migrations completed successfully!" 