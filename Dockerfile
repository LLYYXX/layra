FROM python:3.10-slim

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

# 下载模型
RUN git lfs install && \
    git clone https://hf-mirror.com/vidore/colqwen2.5-base && \
    git clone https://hf-mirror.com/vidore/colqwen2.5-v0.2

# 复制应用代码
COPY . .

# 初始化数据库
RUN alembic upgrade head

# 暴露API端口
EXPOSE 8000

# 启动应用
CMD ["gunicorn", "-c", "gunicorn_config.py", "app.main:app"] 