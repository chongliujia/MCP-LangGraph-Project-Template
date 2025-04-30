# MCP LangGraph 框架

基于LangGraph的多模型控制器规划器(Model-Controller-Planner)框架。

## 简介

MCP框架是一个灵活的、可扩展的大语言模型应用开发框架，专注于将复杂任务分解为可管理的步骤，并提供流畅的执行流程。框架基于三个核心组件：

- **模型层(Model)**: 负责与LLM交互，处理自然语言理解和生成
- **控制器(Controller)**: 控制系统流程，协调各组件间的交互
- **规划器(Planner)**: 负责任务规划、分解和执行策略

## 特性

- 支持多种LLM提供商(OpenAI, DeepSeek等)
- 基于LangGraph的灵活工作流程
- 内置工具系统
- 缓存机制提高性能
- 流式输出支持
- 可配置的日志系统

## 快速开始

### 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

### 配置

创建config.json文件：

```json
{
  "model": "deepseek-chat",
  "temperature": 0.1,
  "provider": "deepseek"
}
```

### 运行示例

```bash
# 使用DeepSeek模型
python main.py --query "你好" --provider deepseek

# 使用OpenAI模型
python main.py --query "你好" --provider openai
```

## 项目结构

```
mcp_langgraph_framework/
├── config.json          # 配置文件
├── main.py              # 主程序入口
├── requirements.txt     # 依赖项
├── src/                 # 源代码
│   ├── agents/          # Agent实现
│   ├── models/          # 模型层实现
│   ├── controllers/     # 控制器实现
│   ├── planners/        # 规划器实现
│   ├── tools/           # 工具实现
│   ├── utils/           # 工具函数
│   └── config/          # 配置管理
└── examples/            # 示例代码
```

## 高级用法

请参考相应的文档：

- [模型层文档](./models.md)
- [控制器文档](./controllers.md)
- [规划器文档](./planners.md)
- [工具系统文档](./tools.md)
- [配置管理文档](./config.md)
- [缓存机制文档](./cache.md)
- [流式输出文档](./streaming.md)

## 贡献

欢迎提交问题和PR以改进框架。

## 许可证

MIT 