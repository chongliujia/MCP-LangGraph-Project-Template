FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY pyproject.toml .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY mcp_framework/ ./mcp_framework/
COPY examples/ ./examples/
COPY env.example .env

# 设置环境变量
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from mcp_framework import MCPFramework; asyncio.run(MCPFramework().health_check())" || exit 1

# 启动命令
CMD ["python", "-m", "mcp_framework.cli", "serve", "--host", "0.0.0.0", "--port", "8000"] 