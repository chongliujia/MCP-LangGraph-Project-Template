# 流式输出文档

MCP框架支持流式输出，可以实时获取LLM生成的内容，提升用户体验。

## 流式输出原理

流式输出允许在模型生成过程中实时获取部分生成内容，而不是等待完整响应：

1. 客户端发送请求，指定使用流式输出
2. 模型开始生成内容，并以数据块(chunks)形式返回
3. 每个数据块包含部分内容，可以立即展示
4. 最后一个数据块标记生成完成

## 核心组件

### StreamingManager

`StreamingManager`是流式响应管理器，负责控制和管理流式输出：

```python
from src.models import streaming_manager

# 启用/禁用流式输出
streaming_manager.set_enabled(True)

# 检查是否启用流式输出
is_enabled = streaming_manager.is_enabled()

# 转换流式输出
async def transform_chunk(chunk):
    chunk["content"] = chunk.get("content", "").upper()
    return chunk

transformed_stream = streaming_manager.transform_stream(
    raw_stream,
    transform_func=transform_chunk
)

# 收集流式输出为完整响应
full_response = await streaming_manager.collect_stream(stream)

# 将流式输出发送到回调函数
def on_chunk(chunk):
    print(chunk.get("content", ""), end="", flush=True)

full_response = await streaming_manager.stream_to_callback(
    stream,
    callback=on_chunk
)
```

### StreamBuffer

`StreamBuffer`是流缓冲区，用于管理流式输出的状态：

```python
from src.models import StreamBuffer

# 创建流缓冲区
buffer = StreamBuffer()

# 添加数据块
await buffer.add_chunk({"content": "你好，"})
await buffer.add_chunk({"content": "我是"})
await buffer.add_chunk({"content": "AI助手"})

# 标记流已完成
await buffer.mark_complete()

# 获取流式输出
async for chunk in buffer.get_stream():
    print(chunk.get("content", ""), end="", flush=True)

# 获取完整内容（等待流完成）
full_content = await buffer.get_full_content()
```

### StreamingChunk

`StreamingChunk`是流式输出的单个数据块的标准格式：

```python
from src.models import StreamingChunk

chunk = StreamingChunk(
    content="你好，",
    tool_calls=None,
    metadata={"tokens": 1},
    is_last=False
)
```

## 使用流式输出

### 基本用法

要使用流式输出，需要在请求中指定`stream=True`：

```python
from src.models import ModelFactory, ModelInput

# 创建模型实例
model = ModelFactory.create_model("deepseek")

# 创建流式请求
input_data = ModelInput(
    messages=[{"role": "user", "content": "写一首诗"}],
    stream=True  # 启用流式输出
)

# 使用流式生成
async for chunk in model.generate_stream(input_data):
    print(chunk.content, end="", flush=True)
```

### 与Web应用集成

在Web应用中使用流式输出示例(FastAPI)：

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from src.models import ModelFactory, ModelInput

app = FastAPI()

@app.post("/chat/stream")
async def stream_chat(request: Request):
    data = await request.json()
    
    # 创建模型实例
    model = ModelFactory.create_model(data.get("provider", "deepseek"))
    
    # 准备输入
    input_data = ModelInput(
        messages=data.get("messages", []),
        system_prompt=data.get("system_prompt"),
        stream=True
    )
    
    # 流式响应生成器
    async def generate():
        async for chunk in model.generate_stream(input_data):
            yield f"data: {json.dumps({'content': chunk.content})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### 客户端接收示例

JavaScript客户端接收流式输出示例：

```javascript
// 发送请求并处理流式响应
async function streamChat() {
    const response = await fetch('/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            provider: 'deepseek',
            messages: [{ role: 'user', content: '写一首诗' }]
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // 处理接收到的数据块
        const lines = buffer.split('\n\n');
        buffer = lines.pop();
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') break;
                
                try {
                    const chunk = JSON.parse(data);
                    // 添加到UI
                    appendToChat(chunk.content);
                } catch (e) {
                    console.error('Error parsing chunk:', e);
                }
            }
        }
    }
}
```

## 配置选项

通过以下配置项控制流式输出行为：

- `streaming_enabled`: 是否启用流式输出 (true/false)
- `streaming_chunk_size`: 流式输出数据块大小限制 (字节)

示例配置：

```json
{
  "streaming_enabled": true,
  "streaming_chunk_size": 1024
}
```

## 注意事项

1. **API支持**: 并非所有模型提供商都支持流式输出
2. **工具调用**: 使用工具调用时，流式输出可能受到限制
3. **缓存**: 流式输出与缓存机制兼容，但可能会引入轻微延迟
4. **错误处理**: 流式输出中的错误处理需要特别注意，以防流中断 