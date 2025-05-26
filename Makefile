.PHONY: help install dev-install test lint format clean docker-build docker-run setup

# 默认目标
help:
	@echo "MCP AI Framework - 可用命令:"
	@echo "  install      - 安装项目依赖"
	@echo "  dev-install  - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理临时文件"
	@echo "  setup        - 初始化项目设置"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run   - 运行Docker容器"
	@echo "  docker-up    - 启动完整服务栈"
	@echo "  docker-down  - 停止服务栈"

# 安装核心依赖
install:
	pip install -r requirements.txt

# 安装开发依赖
dev-install:
	pip install -e ".[dev]"

# 安装向量数据库依赖
install-vector:
	pip install -e ".[vector]"

# 安装AI模型依赖
install-ai:
	pip install -e ".[ai]"

# 安装UI依赖
install-ui:
	pip install -e ".[ui]"

# 安装所有依赖
install-all:
	pip install -e ".[all]"

# 运行测试
test:
	pytest tests/ -v

# 代码检查
lint:
	mypy mcp_framework/
	black --check mcp_framework/
	isort --check-only mcp_framework/

# 代码格式化
format:
	black mcp_framework/
	isort mcp_framework/

# 清理临时文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# 初始化项目设置
setup:
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "已创建 .env 文件，请编辑并设置你的API密钥"; \
	else \
		echo ".env 文件已存在"; \
	fi
	@mkdir -p logs
	@echo "项目设置完成"

# Docker相关命令
docker-build:
	docker build -t mcp-ai-framework .

docker-run:
	docker run -p 8000:8000 --env-file .env mcp-ai-framework

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f mcp-framework

# 启动开发服务器
dev-server:
	python -m mcp_framework.cli serve --debug

# 运行示例
example:
	cd examples && python basic_usage.py

# 运行LangGraph示例
example-langgraph:
	cd examples && python langgraph_example.py

# 健康检查
health:
	python -m mcp_framework.cli health

# 列出模型
list-models:
	python -m mcp_framework.cli list-models

# 列出工具
list-tools:
	python -m mcp_framework.cli list-tools 