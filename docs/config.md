# 配置管理文档

MCP框架提供了灵活的多级配置管理系统，支持从多个来源获取配置，并具有优先级处理和动态更新能力。

## 配置体系

配置管理系统支持从以下来源获取配置（按优先级从高到低）：

1. 命令行参数
2. 环境变量
3. 特定环境配置文件 (config.{env}.json)
4. 基础配置文件 (config.json)
5. 代码中的默认值

## 核心组件

### ConfigManager

ConfigManager是配置管理的核心类，负责加载、合并和提供配置：

```python
from src.config import ConfigManager

# 创建配置管理器
config_manager = ConfigManager(
    config_path="config.json",
    env="development"  # 也可以是 "production" 或 "testing"
)

# 获取配置项
api_key = config_manager.get("deepseek_api_key")
model = config_manager.get("model", "deepseek-chat")  # 提供默认值

# 设置配置项
config_manager.set("temperature", 0.7)

# 保存配置
config_manager.save()
```

### 全局配置函数

为了方便使用，框架提供了全局配置函数：

```python
from src.config import get_config, set_config, save_config

# 获取配置
model = get_config("model", "deepseek-chat")

# 设置配置
set_config("temperature", 0.7)

# 保存配置
save_config()
```

## 配置文件格式

配置文件使用JSON格式，示例：

```json
{
  "model": "deepseek-chat",
  "temperature": 0.1,
  "provider": "deepseek",
  "log_level": "INFO",
  "cache_enabled": true,
  "streaming_enabled": false
}
```

## 环境特定配置

框架支持针对不同环境的配置文件：

- `config.json`: 基础配置
- `config.development.json`: 开发环境配置
- `config.testing.json`: 测试环境配置
- `config.production.json`: 生产环境配置

环境特定配置会覆盖基础配置中的同名项。

## 敏感信息管理

为了安全处理API密钥等敏感信息，框架将其存储在单独的文件中，位于`.secrets`目录：

- `.secrets/secrets.development.json`
- `.secrets/secrets.testing.json`
- `.secrets/secrets.production.json`

这些文件应该被添加到`.gitignore`中以防止意外提交。

示例格式：

```json
{
  "openai_api_key": "sk-...",
  "deepseek_api_key": "sk-..."
}
```

## 环境变量配置

框架支持通过环境变量设置配置，使用`MCP_`前缀：

```bash
# 设置模型
export MCP_MODEL="gpt-4o"

# 设置温度
export MCP_TEMPERATURE="0.5"

# 设置API密钥
export OPENAI_API_KEY="sk-..."
export DEEPSEEK_API_KEY="sk-..."
```

## 配置项

以下是框架支持的主要配置项：

### 基本配置
- `model`: 使用的模型名称
- `provider`: 模型提供商 ("openai", "deepseek", etc.)
- `temperature`: 温度参数 (0.0-1.0)
- `max_tokens`: 最大生成token数

### 模型特定配置
- `openai_api_key`: OpenAI API密钥
- `deepseek_api_key`: DeepSeek API密钥
- `qianwen_api_key`: 通义千问API密钥

### 性能配置
- `cache_enabled`: 是否启用缓存 (true/false)
- `streaming_enabled`: 是否启用流式输出 (true/false)
- `timeout`: API请求超时时间 (秒)

### 日志配置
- `log_level`: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_format`: 日志格式 (text/json)
- `log_file`: 日志文件路径 