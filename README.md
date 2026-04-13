# Intelligent-Travel-Planning-Assistant - 基于多智能体协作的智能旅游规划助手

## 📖 项目简介

Intelligent-Travel-Planning-Assistant 是一个采用**多智能体协作架构**的智能旅游规划平台，通过解耦的 Agent 系统实现端到端的旅行方案生成与动态优化。系统创新性地将 MCP（Model Context Protocol）协议应用于旅行场景，构建了包含意图识别、行程规划、地理编码、记忆管理的完整 AI Pipeline，解决了传统单体架构在可扩展性、维护性和智能化程度上的痛点。

本项目不仅实现了自然语言驱动的交互式旅行规划，更通过**高内聚低耦合**的微服务设计理念，为复杂 AI 应用场景提供了可复用的工程化解决方案。

---

## 🎯 核心功能

### 1. 智能意图解析引擎
- **多模态意图识别**：基于 LLM + 规则混合策略，精准区分闲聊、旅行规划、行程修改三类意图
- **上下文感知路由**：结合对话历史与当前状态，实现智能化的任务分发
- **容错降级机制**：LLM 异常时自动切换至关键词匹配，保证系统可用性

### 2. 多阶段旅行规划 Pipeline
```
用户输入 → Coordinator(意图识别) → TravelPlanner(行程生成) 
         → GeoCoder(坐标修正) → MemoryManager(状态持久化) → 结果整合
```
- **结构化行程生成**：LLM 输出标准化 JSON 格式，包含景点名称、时间分配、描述信息
- **地理坐标智能校正**：集成高德地图 API，批量修正地点经纬度，支持 POI 搜索优化
- **增量式行程修改**：支持添加/删除/调整景点，保持上下文一致性

### 3. 分布式记忆管理系统
- **双层存储架构**：内存缓存（快速访问）+ JSON 文件持久化（断电恢复）
- **对话历史追踪**：完整记录交互过程，支持多轮对话上下文理解
- **状态快照机制**：实时保存当前行程，支持会话中断后恢复

### 4. 可视化地图交互界面
- **动态路线渲染**：基于 Pigeon Maps 实现行程轨迹可视化
- **响应式设计**：适配桌面端与移动端，流畅的拖拽交互体验
- **实时数据同步**：前端组件与后端智能体状态双向绑定

---

## 💡 技术亮点

### 🏗️ 架构设计创新

#### 1. 多智能体协作架构（Multi-Agent System）
- **职责分离原则**：4 个专用智能体各司其职，避免单体应用的"上帝类"问题
  - `CoordinatorAgent`：系统大脑，负责任务调度与结果整合
  - `TravelPlannerAgent`：专注行程生成与优化逻辑
  - `GeoCoderAgent`：纯地理信息服务，无业务耦合
  - `MemoryManagerAgent`：通用状态管理，可复用至其他场景
- **松耦合通信**：通过 MessageBus 实现发布-订阅模式，智能体间零直接依赖
- **热插拔扩展**：新增智能体只需注册到消息总线，无需修改现有代码

#### 2. 自定义 MCP 协议（Model Context Protocol）
```python
{
    "message_id": "uuid",           # 消息追踪
    "message_type": "request",      # request/response/notification/error
    "sender": "coordinator",        # 发送者标识
    "receiver": "travel_planner",   # 目标智能体
    "action": "generate_plan",      # 动作指令
    "payload": {...},               # 业务数据
    "priority": "high",             # 优先级控制
    "timestamp": "ISO8601"          # 时序保证
}
```
- **标准化消息格式**：统一的请求/响应契约，降低集成复杂度
- **异步消息传递**：基于 asyncio 的非阻塞通信，提升并发性能
- **消息历史追溯**：内置调试工具，支持全链路问题定位

### 🤖 算法与模型优化

#### 1. 混合意图识别策略
- **第一层**：关键词快速匹配（修改操作检测）
- **第二层**：LLM 语义分析（复杂意图理解）
- **降级方案**：规则兜底保证系统鲁棒性

#### 2. 智能地理编码优化
- **批量处理**：一次请求处理多个地点，减少 API 调用次数
- **POI 智能选择**：根据地址提示自动选择最佳匹配结果
- **缓存机制预留**：高频地点坐标可接入 Redis 缓存层



---

## 🛠️ 技术栈

### 后端技术
- **Web 框架**：FastAPI 0.109+（异步高性能 API）
- **AI 模型**：通义千问 qwen-plus（阿里云 DashScope）
- **地图服务**：高德地图 Web Service API（地理编码/POI 搜索）
- **数据验证**：Pydantic v2（类型安全的数据模型）
- **异步运行时**：asyncio + uvicorn（ASGI 服务器）
- **配置管理**：pydantic-settings（环境变量自动加载）

### 前端技术
- **核心框架**：React 18.3 + TypeScript 5.x
- **构建工具**：Vite 6.3（极速开发体验）
- **UI 组件库**：
  - Material-UI (MUI) 7.3（企业级组件）
  - shadcn/ui（基于 Radix UI 的可定制组件）
  - Lucide React（现代化图标库）
- **地图渲染**：Pigeon Maps（轻量级 React 地图组件）
- **样式方案**：Tailwind CSS 4.x（原子化 CSS）
- **状态管理**：React Hooks + Context API
- **动画库**：Framer Motion（流畅交互动画）

### 开发工具
- **包管理**：npm / pnpm
- **代码规范**：ESLint + Prettier（前端）
- **版本控制**：Git
- **API 测试**：FastAPI 内置 Swagger UI (`/docs`)

---

## ⚙️ 环境依赖与配置

### 系统要求
- **Python**：3.8+
- **Node.js**：16+
- **操作系统**：Windows / macOS / Linux

### 后端环境配置

#### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 2. 配置环境变量
编辑 `backend/.env` 文件：
```env
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 通义千问 API（必需）
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=sk-your-api-key-here
QWEN_MODEL=qwen-plus

# 高德地图 API（必需）
AMAP_API_KEY=your-amap-web-service-key

# CORS 配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

**获取 API Key：**
- 通义千问：[阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
- 高德地图：[高德开放平台](https://console.amap.com/dev/key/app)

### 前端环境配置

#### 1. 安装依赖
```bash
cd frontend
npm install
# 或使用 pnpm
pnpm install
```

#### 2. 配置后端地址（可选）
默认连接 `http://localhost:8000`，如需修改请编辑前端代码中的 API 基础 URL。

---

## 🚀 前端部署与运行

### 开发模式
```bash
cd frontend
npm run dev
```
访问：`http://localhost:5173`

### 生产构建
```bash
npm run build
# 生成的静态文件在 dist/ 目录
```

### 预览生产构建
```bash
npm run preview
```

---

## 🚀 后端部署与运行

### 方式一：手动启动
```bash
cd backend
python main.py
```

### 方式二：使用 Uvicorn 命令行
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
---

## 🔮 未来演进方向

### 短期优化（1-3 个月）
- [ ] 引入 Redis 缓存层，优化高频查询性能
- [ ] 实现智能体重试机制与熔断器模式
- [ ] 添加 Prometheus + Grafana 监控告警
- [ ] 优化消息序列化（Protocol Buffers）

### 中期扩展（3-6 个月）
- [ ] 引入分布式消息队列（RabbitMQ/Kafka）
- [ ] 支持智能体动态发现与负载均衡
- [ ] 添加专业智能体（天气预报、交通路况、预算规划）
- [ ] 实现多用户会话隔离与权限管理

### 长期愿景（6-12 个月）
- [ ] 容器化部署（Docker + Kubernetes）
- [ ] 微服务拆分（独立部署各智能体）
- [ ] 支持插件市场（第三方智能体接入）
- [ ] 多语言国际化支持

---

**用 AI 重新定义旅行规划体验** 🌍✈️🤖
