FROM python:3.10-slim-bullseye

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建migrations目录（如果不存在）并初始化alembic
RUN mkdir -p migrations && \
    if [ ! -f migrations/env.py ]; then alembic init migrations; fi

# 执行数据库迁移
RUN alembic upgrade head || echo "Database migration skipped, will be handled during runtime"

# 暴露API端口
EXPOSE 8000

# 启动应用
CMD ["gunicorn", "-c", "gunicorn_config.py", "app.main:app"] 