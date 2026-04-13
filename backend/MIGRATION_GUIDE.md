# 多智能体架构迁移指南

## 📌 概述

本文档说明如何将原有的单体服务架构迁移到多智能体协作架构。

---

## 🔄 架构对比

### 原有架构（单体式）

```
API Routes → TravelService → LLM Service + Geocoding Service
```

**特点**：
- ✅ 简单直接
- ❌ 耦合度高
- ❌ 难以扩展
- ❌ 职责不清晰

### 新架构（多智能体）

```
API Routes → Coordinator Agent → [TravelPlanner, GeoCoder, MemoryManager]
                ↑
          Message Bus (MCP Protocol)
```

**特点**：
- ✅ 高内聚低耦合
- ✅ 易于扩展
- ✅ 职责清晰
- ✅ 可独立测试

---

## 📂 文件变更清单

### 新增文件

```
backend/
├── agents/                          # 新增：智能体模块
│   ├── __init__.py
│   ├── mcp_protocol.py             # MCP协议定义
│   ├── message_bus.py              # 消息总线
│   ├── coordinator_agent.py        # 协调者智能体
│   ├── travel_planner_agent.py     # 旅行规划智能体
│   ├── geo_coder_agent.py          # 地理编码智能体
│   └── memory_manager_agent.py     # 记忆管理智能体
├── data/
│   └── memory/                     # 新增：数据存储目录
│       └── current_state.json      # 自动创建
├── test_multi_agent.py             # 新增：测试脚本
└── MULTI_AGENT_ARCHITECTURE.md     # 新增：架构文档
```

### 修改文件

```
backend/
├── main.py                         # 修改：添加智能体初始化
├── routes/
│   └── chat_routes.py              # 修改：使用消息总线通信
```

### 保留文件（向后兼容）

```
backend/
├── services/
│   ├── llm_service.py              # 保留：被智能体复用
│   ├── geocoding_service.py        # 保留：被智能体复用
│   └── travel_service.py           # 保留：暂时不用，可删除
├── models.py                       # 保留：数据模型
├── config.py                       # 保留：配置
└── requirements.txt                # 保留：依赖
```

---

## 🚀 迁移步骤

### 步骤1：安装依赖（无需额外依赖）

新架构使用现有的依赖，无需安装新包：

```bash
pip install -r requirements.txt
```

### 步骤2：启动服务

```bash
cd backend
python main.py
```

你会看到：

```
============================================================
🤖 多智能体系统初始化中...
============================================================
✅ 已注册 4 个智能体:
   - coordinator
   - travel_planner
   - geo_coder
   - memory_manager
============================================================
🚀 系统就绪！

🚀 旅行地图AI助手启动中...
...
```

### 步骤3：运行测试

```bash
python test_multi_agent.py
```

预期输出：

```
🧪 🧪 🧪 ...
多智能体系统测试套件
🧪 🧪 🧪 ...

============================================================
测试1：智能体注册
============================================================
✅ 已注册 4 个智能体:
   - coordinator
   - travel_planner
   - geo_coder
   - memory_manager
✅ 所有智能体已成功注册

...

============================================================
测试结果汇总
============================================================
✅ 通过 - 智能体注册
✅ 通过 - MCP消息格式
✅ 通过 - 协调者意图识别
✅ 通过 - 旅行规划智能体
✅ 通过 - 记忆管理智能体
✅ 通过 - 完整工作流程
============================================================
总计: 6/6 测试通过
🎉 所有测试通过！
```

### 步骤4：验证API功能

前端无需修改，API接口保持兼容：

```bash
# 健康检查
curl http://localhost:8000/health

# 查看智能体状态
curl http://localhost:8000/agents/status

# 测试聊天接口
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "推荐北京两日游"}
    ]
  }'
```

---

## 🔍 关键变化说明

### 1. 路由层变化

**原代码** (`chat_routes.py`):
```python
from services.travel_service import travel_service

result = await travel_service.process_chat_message(
    user_input=user_message.content,
    conversation_history=conversation_history
)
```

**新代码**:
```python
from agents.mcp_protocol import MCPMessage, MessageType, MessagePriority
from agents.message_bus import message_bus

mcp_message = MCPMessage(
    message_id=str(uuid.uuid4()),
    message_type=MessageType.REQUEST,
    sender="api_gateway",
    receiver="coordinator",
    action="process_user_input",
    payload={
        "user_input": user_message.content,
        "conversation_history": conversation_history
    },
    priority=MessagePriority.HIGH
)

response = await message_bus.send_message(mcp_message)
result = response.data
```

### 2. 服务层变化

**原有**：`TravelService` 直接调用 `llm_service` 和 `geocoding_service`

**新架构**：
- `TravelPlannerAgent` 调用 `llm_service`
- `GeoCoderAgent` 调用 `geocoding_service`
- `CoordinatorAgent` 通过消息总线调度各智能体

### 3. 状态管理变化

**原有**：`TravelService.current_itinerary` 内存变量

**新架构**：`MemoryManagerAgent` 统一管理，支持持久化

---

## ⚙️ 配置调整

### 环境变量（无需修改）

`.env` 文件保持不变：

```env
QWEN_API_KEY=your_api_key
AMAP_API_KEY=your_amap_key
HOST=0.0.0.0
PORT=8000
```

### 日志配置（可选优化）

在 `main.py` 中添加日志配置：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 设置不同智能体的日志级别
logging.getLogger("agents.coordinator_agent").setLevel(logging.DEBUG)
logging.getLogger("agents.travel_planner_agent").setLevel(logging.INFO)
```

---

## 🧪 测试策略

### 单元测试

每个智能体可独立测试：

```python
# test_coordinator_agent.py
import pytest
from agents.coordinator_agent import coordinator_agent

@pytest.mark.asyncio
async def test_intent_recognition():
    intent = await coordinator_agent._analyze_intent("你好", [])
    assert intent == "chat"
```

### 集成测试

测试智能体间协作：

```python
# test_agent_collaboration.py
@pytest.mark.asyncio
async def test_full_workflow():
    response = await message_bus.send_message(MCPMessage(...))
    assert response.success
    assert response.data.get("locations")
```

### 端到端测试

测试完整API流程：

```python
# test_api_e2e.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.post("/api/chat", json={
        "messages": [{"role": "user", "content": "推荐景点"}]
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

---

## 🐛 常见问题

### Q1: 智能体未注册？

**症状**：`message_bus.get_registered_agents()` 返回空列表

**解决**：确保在主程序中导入了所有智能体：
```python
from agents.coordinator_agent import coordinator_agent
from agents.travel_planner_agent import travel_planner_agent
# ...
```

导入时会执行 `__init__`，自动注册到消息总线。

### Q2: 消息发送失败？

**症状**：`response.success == False`，错误信息 "未找到接收者"

**解决**：检查 `receiver` 名称是否正确：
```python
# 正确
receiver="coordinator"

# 错误（会失败）
receiver="Coordinator"  # 大小写敏感
receiver="coord"        # 名称不匹配
```

### Q3: 行程数据丢失？

**症状**：重启服务后行程清空

**解决**：检查 `data/memory/` 目录是否存在且有写权限：
```bash
mkdir -p data/memory
chmod 755 data/memory
```

### Q4: 性能问题？

**症状**：响应速度慢

**优化建议**：
1. 启用异步并发：
```python
# 并行调用多个智能体
responses = await asyncio.gather(
    message_bus.send_message(msg1),
    message_bus.send_message(msg2)
)
```

2. 添加缓存（GeoCoder）：
```python
# 在 GeoCoderAgent 中添加LRU缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_geocode(address: str):
    ...
```

---

## 📊 性能对比

| 指标 | 原架构 | 新架构 | 说明 |
|------|--------|--------|------|
| 首次响应时间 | ~2s | ~2.2s | 增加消息路由开销 |
| 代码行数 | ~500行 | ~900行 | 增加协议和总线代码 |
| 可维护性 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 职责清晰 |
| 可扩展性 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 轻松添加新智能体 |
| 测试难度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 可独立测试 |
| 团队协作 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 并行开发 |

**结论**：轻微的性能开销换取巨大的架构优势。

---

## 🎯 后续优化方向

### 1. 添加更多智能体

```python
# WeatherAgent - 天气查询
# TrafficAgent - 交通状况
# RecommendationAgent - 个性化推荐
# BudgetAgent - 预算规划
```

### 2. 引入消息队列

当前使用内存消息总线，生产环境可替换为：
- Redis Pub/Sub
- RabbitMQ
- Kafka

### 3. 智能体发现机制

实现动态智能体注册和发现：
```python
# 智能体启动时自动广播能力
await message_bus.broadcast(CapabilityAnnouncement(...))
```

### 4. 监控和追踪

集成分布式追踪：
- OpenTelemetry
- Jaeger
- Prometheus监控

---

## 📝 回滚方案

如果遇到问题需要回滚到原架构：

1. 恢复 `chat_routes.py`：
```bash
git checkout HEAD -- routes/chat_routes.py
```

2. 恢复 `main.py`：
```bash
git checkout HEAD -- main.py
```

3. 删除 `agents/` 目录（可选）

原架构仍可正常工作，新旧架构完全兼容。

---

## ✅ 迁移检查清单

- [ ] 已阅读 `MULTI_AGENT_ARCHITECTURE.md`
- [ ] 已安装所有依赖
- [ ] 已运行 `test_multi_agent.py` 并通过所有测试
- [ ] 已启动服务并查看智能体注册信息
- [ ] 已测试API接口（健康检查、聊天、行程）
- [ ] 已验证前端功能正常
- [ ] 已检查日志输出无异常
- [ ] 已备份原有代码（Git提交）
- [ ] 团队已了解新架构设计

---

## 📞 技术支持

如有问题，请查阅：
1. `MULTI_AGENT_ARCHITECTURE.md` - 详细架构说明
2. `agents/mcp_protocol.py` - MCP协议定义
3. `test_multi_agent.py` - 测试用例参考

或联系开发团队。
