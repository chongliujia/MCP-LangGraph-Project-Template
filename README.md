# MCP LangGraph Framework

一个基于 LangChain 和 LangGraph 构建的通用 MCP 框架，提供强大的工作流编排和AI代理能力。

## 🚀 特性

- **🔄 LangGraph工作流**: 基于LangGraph的强大工作流编排
- **🔧 LangChain工具集成**: 完全兼容LangChain工具生态
- **🤖 多模型支持**: 支持DeepSeek、Qwen等多种AI模型
- **🌐 MCP协议**: 完全兼容Model Context Protocol
- **⚡ 异步架构**: 高性能异步处理
- **🧠 智能代理**: 支持多代理协作和复杂推理
- **📊 RAG支持**: 内置检索增强生成能力

## 📁 项目结构

```
mcp_framework/
├── config/           # 配置管理
│   ├── settings.py   # 主要设置
│   ├── model_config.py  # 模型配置
│   └── vector_config.py # 向量数据库配置
├── core/             # 核心框架
│   ├── framework.py  # 主框架类
│   ├── tool_manager.py  # 工具管理器
│   └── mcp_server.py    # MCP服务器
├── models/           # 模型管理
│   └── model_manager.py # 模型管理器
├── vector_db/        # 向量数据库
│   └── milvus_client.py # Milvus客户端
├── tools/            # 工具集合
├── api/              # API接口
├── ui/               # 用户界面
├── utils/            # 工具函数
├── examples/         # 示例代码
└── tests/            # 测试代码
```

## 🛠️ 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd mcp_framework
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
# 或者
pip install -e .
```

### 3. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 4. 启动Milvus (可选)

如果你需要使用向量数据库功能：

```bash
# 使用Docker启动Milvus
docker run -d --name milvus-standalone \
  -p 19530:19530 -p 9091:9091 \
  -v $(pwd)/volumes/milvus:/var/lib/milvus \
  milvusdb/milvus:latest standalone
```

## 🚀 快速开始

### 基本使用

```python
import asyncio
from mcp_framework import MCPLangGraphFramework
from mcp_framework.tools import CalculatorTool, SearchTool

async def main():
    # 初始化框架
    async with MCPLangGraphFramework() as framework:
        # 注册工具
        framework.register_tool(CalculatorTool())
        framework.register_tool(SearchTool())
        
        # 聊天对话
        response = await framework.chat("你好，请计算 15 + 27 * 3")
        print(response)
        
        # 运行自定义工作流
        result = await framework.run_workflow({
            "messages": [{"role": "user", "content": "搜索人工智能相关信息"}]
        })
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 启动MCP服务器

```python
import asyncio
from mcp_framework import MCPFramework

async def main():
    framework = MCPFramework()
    await framework.start_server()

if __name__ == "__main__":
    asyncio.run(main())
```

### 注册自定义工具

```python
from mcp_framework.tools.base import BaseTool

class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "我的自定义工具"
    
    async def execute(self, **kwargs):
        # 工具逻辑
        return "工具执行结果"

# 注册工具
framework.register_tool(MyCustomTool)
```

## 🔧 配置

### 环境变量

主要的环境变量配置：

- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `QWEN_API_KEY`: Qwen API密钥
- `MILVUS_HOST`: Milvus服务器地址
- `MILVUS_PORT`: Milvus端口

详细配置请参考 `env.example` 文件。

### 模型配置

框架支持以下模型：

**聊天模型:**
- `deepseek-chat`: DeepSeek聊天模型
- `deepseek-coder`: DeepSeek代码模型
- `qwen-turbo`: Qwen Turbo模型
- `qwen-plus`: Qwen Plus模型
- `qwen-max`: Qwen Max模型

**嵌入模型:**
- `qwen-embedding`: Qwen嵌入模型
- `qwen-embedding-v2`: Qwen嵌入模型v2

**重排模型:**
- `qwen-rerank`: Qwen重排模型

## 📚 API文档

### MCPFramework 主要方法

- `chat(message, model_name=None, **kwargs)`: 发送聊天消息
- `embed_text(text, model_name=None)`: 生成文本嵌入
- `search_similar(query, top_k=10)`: 搜索相似文档
- `add_document(text, metadata=None)`: 添加文档
- `execute_tool(tool_name, **kwargs)`: 执行工具
- `register_tool(tool_class)`: 注册工具

## 🔌 工具开发

创建自定义工具：

```python
from mcp_framework.tools.base import BaseTool
from typing import Dict, Any

class WeatherTool(BaseTool):
    name = "weather"
    description = "获取天气信息"
    
    parameters = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称"
            }
        },
        "required": ["city"]
    }
    
    async def execute(self, city: str) -> Dict[str, Any]:
        # 实现天气查询逻辑
        return {
            "city": city,
            "temperature": "25°C",
            "condition": "晴天"
        }
```

## 🧪 测试

运行测试：

```bash
pytest tests/
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请提交Issue或联系维护者。
