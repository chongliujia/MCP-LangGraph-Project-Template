# 模型层文档

模型层是MCP框架的核心组件之一，负责与各种LLM提供商的API交互，处理自然语言理解和生成。

## 架构

模型层基于统一的接口设计，通过抽象基类`BaseModelLayer`定义核心功能，各具体模型实现提供实际功能：

```
BaseModelLayer (抽象基类)
├── OpenAIModel (OpenAI模型实现)
├── DeepSeekModel (DeepSeek模型实现)
└── ... (其他模型实现)
```

## 核心组件

### 模型输入/输出

- `ModelInput`: 模型输入的标准格式
- `ModelOutput`: 模型输出的标准格式

### 模型工厂

`ModelFactory`类提供统一的模型创建接口，支持各种LLM提供商：

```python
# 使用工厂创建模型
model = ModelFactory.create_model("deepseek", {
    "api_key": "您的API密钥",
    "temperature": 0.7
})
```

### 流式输出

框架提供流式输出支持，可以实时获取LLM生成的内容：

- `StreamingChunk`: 流式输出的单个数据块
- `StreamingManager`: 流式响应管理器
- `StreamBuffer`: 流缓冲区，用于管理流式输出状态

## 支持的模型

### OpenAI

支持OpenAI的全系列模型，包括GPT-4、GPT-4o等：

```python
from src.models import ModelFactory, ModelInput

model = ModelFactory.create_model("openai", {
    "api_key": "您的OpenAI API密钥"
})

response = await model.generate(ModelInput(
    messages=[{"role": "user", "content": "你好，请介绍一下自己。"}]
))
```

### DeepSeek

支持DeepSeek的模型：

```python
from src.models import ModelFactory, ModelInput

model = ModelFactory.create_model("deepseek", {
    "api_key": "您的DeepSeek API密钥"
})

response = await model.generate(ModelInput(
    messages=[{"role": "user", "content": "你好，请介绍一下自己。"}]
))
```

## 缓存机制

模型层内置了缓存机制，可以缓存模型响应以提高性能：

```python
from src.utils import cached_model_response

# 使用缓存装饰器
@cached_model_response
async def generate(self, input_data):
    # 实现生成逻辑...
```

## 使用流式输出

```python
from src.models import ModelFactory, ModelInput, streaming_manager

# 启用流式输出
streaming_manager.set_enabled(True)

model = ModelFactory.create_model("openai")

# 请求流式响应
input_data = ModelInput(
    messages=[{"role": "user", "content": "请写一个故事"}],
    stream=True  # 启用流式输出
)

# 获取流式响应
async for chunk in model.generate_stream(input_data):
    print(chunk.content, end="", flush=True)
```

## 自定义模型实现

要添加新的模型提供商支持，需要继承`BaseModelLayer`并实现相应的方法：

```python
from src.models import BaseModelLayer, ModelInput, ModelOutput

class CustomModel(BaseModelLayer):
    async def generate(self, input_data: ModelInput) -> ModelOutput:
        # 实现生成逻辑
        
    def generate_sync(self, input_data: ModelInput) -> ModelOutput:
        # 实现同步生成逻辑
        
    # 可选：实现流式生成
    async def generate_stream(self, input_data: ModelInput):
        # 实现流式生成逻辑
```

然后将其添加到`ModelFactory`：

```python
# 在model_factory.py中
MODEL_TYPES = {
    "openai": OpenAIModel,
    "deepseek": DeepSeekModel,
    "custom": CustomModel,  # 添加自定义模型
}
```

## 配置选项

模型层支持的配置选项包括：

- `provider`: 模型提供商 ("openai", "deepseek", etc.)
- `model`: 模型名称
- `api_key`: API密钥
- `temperature`: 温度参数，控制创造性
- `max_tokens`: 最大生成token数
- `cache_enabled`: 是否启用缓存
- `streaming_enabled`: 是否启用流式输出 