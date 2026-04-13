# 多智能体协作架构说明

## 📋 架构概述

本系统采用**多智能体协作 + MCP（Model Context Protocol）协议**架构，实现高内聚低耦合的设计目标。

### 核心设计理念

1. **单一职责原则**：每个智能体专注于一个特定领域
2. **标准化通信**：通过MCP协议进行消息传递
3. **松耦合设计**：智能体之间互不依赖，通过消息总线解耦
4. **易于扩展**：新增智能体只需注册到消息总线即可

---

## 🏗️ 架构图

```
┌──────────────────────────────────────────────────────┐
│                   API Gateway                         │
│              (FastAPI Routes Layer)                   │
└──────────────────────┬───────────────────────────────┘
                       │
                       │ MCP Message
                       ▼
┌──────────────────────────────────────────────────────┐
│              Message Bus (消息总线)                    │
│         - 消息路由                                    │
│         - 异步通信                                    │
│         - 发布-订阅模式                               │
└──┬────────────┬────────────┬────────────┬────────────┘
   │            │            │            │
   ▼            ▼            ▼            ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│Coordi- │ │Travel    │ │GeoCoder  │ │Memory        │
│nator   │ │Planner   │ │Agent     │ │Manager       │
│Agent   │ │Agent     │ │          │ │Agent         │
│        │ │          │ │          │ │              │
│-意图识别│ │-行程生成  │ │-地理编码  │ │-状态管理      │
│-任务分解│ │-景点推荐  │ │-POI搜索  │ │-对话历史      │
│-结果整合│ │-行程修改  │ │-坐标修正  │ │-数据持久化    │
│-调度协调│ │          │ │          │ │              │
└────────┘ └──────────┘ └──────────┘ └──────────────┘
   │            │            │            │
   └────────────┴────────────┴────────────┘
                │
                ▼
        ┌──────────────┐
        │ LLM Service  │
        │ (通义千问)    │
        └──────────────┘
                │
                ▼
        ┌──────────────────┐
        │Geocoding Service │
        │ (高德地图API)     │
        └──────────────────┘
```

---

## 🤖 智能体详解

### 1. Coordinator Agent（协调者智能体）

**职责**：系统的大脑，负责任务调度和结果整合

**核心功能**：
- 意图识别：判断用户是闲聊、旅行规划还是行程修改
- 任务分解：将复杂任务拆解为子任务
- 智能体调度：按顺序调用其他智能体
- 结果整合：汇总各智能体的输出

**支持的动作**：
- `process_user_input`：处理用户输入
- `get_capabilities`：返回能力描述

**示例流程**：
```python
用户输入: "我想去北京玩两天"
↓
Coordinator 分析意图 → travel_planning
↓
调用 TravelPlannerAgent 生成行程
↓
调用 GeoCoderAgent 修正坐标
↓
调用 MemoryManagerAgent 保存状态
↓
整合结果返回给用户
```

---

### 2. Travel Planner Agent（旅行规划智能体）

**职责**：专注于旅行计划的生成和优化

**核心功能**：
- 根据用户需求生成详细行程
- 景点推荐和时间安排
- 行程修改和优化

**支持的动作**：
- `generate_plan`：生成新的旅行计划
- `modify_plan`：修改现有计划
- `get_capabilities`：返回能力描述

**技术实现**：
- 使用通义千问LLM生成结构化JSON行程
- 内置行程修改逻辑
- 支持上下文感知的规划

---

### 3. GeoCoder Agent（地理编码智能体）

**职责**：将地点名称转换为精确的地理坐标

**核心功能**：
- 批量地理编码
- POI搜索和匹配
- 坐标精度优化

**支持的动作**：
- `batch_geocode`：批量处理多个地点
- `single_geocode`：单个地点编码
- `poi_search`：POI搜索
- `get_capabilities`：返回能力描述

**技术实现**：
- 集成高德地图API
- 智能选择最佳POI结果
- 支持地址提示增强准确性

---

### 4. Memory Manager Agent（记忆管理智能体）

**职责**：管理对话历史和系统状态

**核心功能**：
- 行程状态保存和加载
- 对话历史管理
- 数据持久化到文件系统

**支持的动作**：
- `save_itinerary`：保存行程
- `update_itinerary`：更新行程
- `get_itinerary`：获取当前行程
- `clear_itinerary`：清除行程
- `add_conversation`：添加对话记录
- `get_conversation_history`：获取对话历史
- `clear_history`：清除历史
- `get_capabilities`：返回能力描述

**存储机制**：
- 内存缓存：快速访问当前状态
- 文件持久化：`data/memory/current_state.json`
- 自动加载：启动时恢复上次状态

---

## 📨 MCP协议详解

### MCPMessage（消息格式）

所有智能体间的通信都使用统一的MCP消息格式：

```python
{
    "message_id": "uuid",           # 唯一消息ID
    "message_type": "request",      # 消息类型：request/response/notification/error
    "sender": "coordinator",        # 发送者
    "receiver": "travel_planner",   # 接收者
    "action": "generate_plan",      # 动作/命令
    "payload": {...},               # 负载数据
    "priority": "high",             # 优先级：low/normal/high/critical
    "timestamp": "2024-...",        # 时间戳
    "metadata": {...}               # 元数据
}
```

### MCPResponse（响应格式）

```python
{
    "success": true,                # 是否成功
    "data": {...},                  # 响应数据
    "error": null,                  # 错误信息（失败时）
    "message_id": "uuid",           # 关联的请求ID
    "metadata": {...}               # 元数据
}
```

---

## 🔄 消息流转示例

### 场景：用户请求旅行规划

```
1. 用户 → API Gateway
   POST /api/chat
   {
     "messages": [
       {"role": "user", "content": "推荐北京两日游"}
     ]
   }

2. API Gateway → Message Bus
   MCPMessage(
     sender="api_gateway",
     receiver="coordinator",
     action="process_user_input",
     payload={
       "user_input": "推荐北京两日游",
       "conversation_history": []
     }
   )

3. Coordinator → TravelPlanner
   MCPMessage(
     sender="coordinator",
     receiver="travel_planner",
     action="generate_plan",
     payload={...}
   )

4. TravelPlanner → LLM Service
   调用 generate_travel_plan()

5. LLM Service → TravelPlanner
   返回结构化行程JSON

6. TravelPlanner → Coordinator
   MCPResponse(
     success=true,
     data={
       "response": "...",
       "locations": [...],
       "itinerary_title": "..."
     }
   )

7. Coordinator → GeoCoder
   MCPMessage(
     sender="coordinator",
     receiver="geo_coder",
     action="batch_geocode",
     payload={"locations": [...]}
   )

8. GeoCoder → Geocoding Service
   调用 batch_geocode()

9. Geocoding Service → GeoCoder
   返回修正后的坐标

10. GeoCoder → Coordinator
    MCPResponse(
      success=true,
      data=[修正后的地点列表]
    )

11. Coordinator → MemoryManager
    MCPMessage(
      sender="coordinator",
      receiver="memory_manager",
      action="save_itinerary",
      payload={...}
    )

12. MemoryManager → Coordinator
    MCPResponse(success=true)

13. Coordinator → API Gateway
    MCPResponse(
      success=true,
      data={最终结果}
    )

14. API Gateway → 用户
    {
      "response": "...",
      "locations": [...],
      "itinerary_title": "..."
    }
```

---

## 🎯 高内聚低耦合实现

### 高内聚（High Cohesion）

每个智能体内部高度聚焦：

✅ **TravelPlannerAgent**
- 只负责行程生成和修改
- 不涉及地理编码细节
- 不管理持久化状态

✅ **GeoCoderAgent**
- 只负责坐标转换
- 不知道行程是什么
- 纯粹的地理信息服务

✅ **MemoryManagerAgent**
- 只负责状态管理
- 不参与业务逻辑
- 提供通用的CRUD接口

### 低耦合（Low Coupling）

智能体之间通过标准接口通信：

✅ **无直接依赖**
- 智能体A不需要import智能体B
- 通过MessageBus间接通信
- 可以独立测试和替换

✅ **标准化协议**
- 所有通信使用MCPMessage
- 统一的请求/响应格式
- 清晰的接口契约

✅ **动态注册**
```python
# 智能体只需注册到消息总线
message_bus.register_agent(agent_name, handler)

# 其他智能体通过名称发送消息
await message_bus.send_message(MCPMessage(
    receiver="target_agent",
    action="some_action",
    payload={...}
))
```

---

## 🚀 如何扩展新智能体

### 步骤1：创建智能体类

```python
# agents/weather_agent.py
from agents.mcp_protocol import MCPMessage, MCPResponse
from agents.message_bus import message_bus

class WeatherAgent:
    def __init__(self):
        self.agent_name = "weather_agent"
        message_bus.register_agent(self.agent_name, self.handle_message)
    
    async def handle_message(self, message: MCPMessage) -> MCPResponse:
        if message.action == "get_weather":
            return await self._get_weather(message.payload)
        # ...
    
    async def _get_weather(self, payload: Dict) -> MCPResponse:
        # 实现天气查询逻辑
        pass

weather_agent = WeatherAgent()
```

### 步骤2：在主程序中导入

```python
# main.py
from agents.weather_agent import weather_agent  # 自动注册
```

### 步骤3：在协调者中调用

```python
# coordinator_agent.py
weather_response = await message_bus.send_message(MCPMessage(
    sender=self.agent_name,
    receiver="weather_agent",
    action="get_weather",
    payload={"city": "北京"}
))
```

**完成！** 无需修改其他智能体代码。

---

## 📊 性能优势

### 1. 并行处理潜力
```python
# 可以同时调用多个智能体
responses = await asyncio.gather(
    message_bus.send_message(msg_to_geo_coder),
    message_bus.send_message(msg_to_weather_agent),
    message_bus.send_message(msg_to_traffic_agent)
)
```

### 2. 独立扩展
- 可以将繁忙的智能体部署到独立服务器
- 只需修改MessageBus的路由逻辑

### 3. 缓存优化
- MemoryManager可以添加Redis缓存
- GeoCoder可以缓存常用地点坐标

---

## 🔧 调试和监控

### 查看智能体状态
```bash
GET /agents/status
```

返回：
```json
{
  "registered_agents": [
    "coordinator",
    "travel_planner",
    "geo_coder",
    "memory_manager"
  ],
  "message_history_count": 156
}
```

### 消息历史追踪
```python
# 在代码中查看最近的消息
history = message_bus.get_message_history(limit=10)
for msg in history:
    print(f"{msg.sender} -> {msg.receiver}: {msg.action}")
```

### 日志输出
每个智能体都有独立的logger：
```python
logger = logging.getLogger(__name__)  # agents.coordinator_agent
```

---

## 📝 总结

### 架构优势

✅ **高内聚**：每个智能体职责明确，内部逻辑紧凑  
✅ **低耦合**：通过消息总线解耦，无直接依赖  
✅ **易扩展**：新增智能体只需注册，不影响现有代码  
✅ **可测试**：智能体可独立单元测试  
✅ **可维护**：问题定位清晰，修改影响范围小  
✅ **灵活性**：支持动态添加/移除智能体  

### 适用场景

- ✅ 复杂业务流程分解
- ✅ 多服务协同工作
- ✅ 需要灵活扩展的系统
- ✅ 团队协作开发（不同人负责不同智能体）

### 技术栈

- **框架**：FastAPI + Python 3.8+
- **通信**：自定义MCP协议
- **LLM**：通义千问（阿里云）
- **地图**：高德地图API
- **存储**：JSON文件（可扩展为数据库）

---

## 📚 相关文件

- `agents/mcp_protocol.py` - MCP协议定义
- `agents/message_bus.py` - 消息总线实现
- `agents/coordinator_agent.py` - 协调者智能体
- `agents/travel_planner_agent.py` - 旅行规划智能体
- `agents/geo_coder_agent.py` - 地理编码智能体
- `agents/memory_manager_agent.py` - 记忆管理智能体
- `routes/chat_routes.py` - API路由（已适配多智能体）
- `main.py` - 主程序（智能体初始化）
