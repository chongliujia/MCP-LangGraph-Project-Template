# 缓存机制文档

MCP框架提供了强大的缓存系统，旨在提高性能并减少对LLM API的重复调用。

## 缓存体系

缓存系统包含以下核心组件：

- **通用缓存**: 基础缓存实现，支持内存存储和过期策略
- **模型响应缓存**: 专为LLM响应设计的缓存，支持内存和磁盘双级存储
- **缓存装饰器**: 用于方便地为函数添加缓存功能

## 核心组件

### Cache

`Cache`是通用缓存实现，提供基础缓存功能：

```python
from src.utils import Cache

# 创建缓存实例
cache = Cache(
    max_size=1000,       # 最大缓存条目数
    ttl=3600,            # 缓存生存时间（秒）
    eviction_policy="lru" # 清理策略 (lru, lfu, fifo)
)

# 设置缓存项
cache.set("key1", "value1")

# 获取缓存项
value = cache.get("key1")

# 设置带自定义TTL的缓存项
cache.set("key2", "value2", ttl=600)  # 10分钟

# 删除缓存项
cache.delete("key1")

# 清空缓存
cache.clear()

# 清理过期项
cache.cleanup_expired()

# 获取缓存统计
stats = cache.get_stats()
```

### ModelResponseCache

`ModelResponseCache`专为LLM响应设计，提供内存和磁盘双级缓存：

```python
from src.utils import ModelResponseCache

# 创建模型响应缓存
cache = ModelResponseCache(
    cache_dir="./cache/models",  # 缓存目录
    max_memory_items=1000,       # 内存缓存最大条目数
    memory_ttl=3600,             # 内存缓存生存时间（秒）
    disk_ttl=86400 * 7,          # 磁盘缓存生存时间（秒）
    use_disk=True                # 是否使用磁盘缓存
)

# 获取缓存响应
response = cache.get(
    provider="deepseek",
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
    system_prompt="你是一个助手"
)

# 缓存响应
cache.set(
    provider="deepseek",
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
    response=model_response,
    system_prompt="你是一个助手"
)

# 清理过期缓存
memory_cleaned, disk_cleaned = cache.cleanup()

# 清空所有缓存
cache.clear()
```

### 缓存装饰器

`cached_model_response`装饰器可以自动为模型生成函数添加缓存功能：

```python
from src.utils import cached_model_response

class MyModel(BaseModelLayer):
    @cached_model_response
    async def generate(self, input_data: ModelInput) -> ModelOutput:
        # 实现生成逻辑...
```

## 全局缓存实例

框架提供了全局缓存实例`model_cache`，可以直接使用：

```python
from src.utils import model_cache

# 获取缓存响应
response = model_cache.get(
    provider="deepseek",
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}]
)
```

## 缓存配置

可以通过以下配置项控制缓存行为：

- `cache_enabled`: 是否启用缓存 (true/false)
- `cache_memory_size`: 内存缓存大小
- `cache_memory_ttl`: 内存缓存生存时间（秒）
- `cache_disk_ttl`: 磁盘缓存生存时间（秒）
- `cache_dir`: 缓存目录路径

示例配置：

```json
{
  "cache_enabled": true,
  "cache_memory_size": 2000,
  "cache_memory_ttl": 7200,
  "cache_disk_ttl": 604800,
  "cache_dir": "./cache"
}
```

## 缓存键计算

缓存系统会根据以下因素计算缓存键：

- 模型提供商
- 模型名称
- 消息内容
- 系统提示
- 温度参数 (temperature)
- 其他影响输出的参数 (top_p, top_k, max_tokens等)

## 注意事项

1. **确定性请求**: 只有确定性请求(temperature=0)才会被缓存
2. **磁盘空间**: 长期使用可能占用大量磁盘空间，定期清理很重要
3. **缓存有效性**: 如果模型有更新，缓存的响应可能不是最新的
4. **并发安全**: 缓存实现是线程安全的，可以在并发环境中使用 