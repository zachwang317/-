FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/work/logs/bypass /app/assets

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV PYTHONPATH=/app
ENV COZE_PROJECT_ENV=PROD

# 启动HTTP服务
CMD ["bash", "scripts/http_run.sh", "-m", "http", "-p", "5000"]
