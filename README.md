# MCP LangGraph Framework

一个基于MCP（Model-Controller-Planner）协议架构的AI系统框架，使用LangGraph构建。

## 架构概述

本框架采用MCP架构：
- **Model**: 负责与LLM交互，处理自然语言理解和生成
- **Controller**: 控制系统流程，协调各组件间的交互
- **Planner**: 负责任务规划、分解和执行策略

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python main.py
```

## 项目结构

```
.
├── README.md
├── requirements.txt
├── main.py
├── .env.example
├── src/
│   ├── __init__.py
│   ├── models/         # 模型层实现
│   ├── controllers/    # 控制器层实现
│   ├── planners/       # 规划器层实现
│   ├── agents/         # 组合型agent实现
│   ├── tools/          # 工具集
│   └── utils/          # 通用工具函数
└── examples/           # 使用示例
``` # MCP-LangGraph-Project-Template
