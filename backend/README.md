# 旅行地图后端服务

智能旅游规划助手的后端服务，基于 FastAPI 构建。

## 📁 项目结构

```
backend/
├── config.py              # 配置管理
├── models.py              # 数据模型定义
├── main.py                # FastAPI 应用入口
├── requirements.txt       # Python 依赖包
├── .env                   # 环境变量配置
├── .env.example           # 环境变量示例
├── .gitignore            # Git 忽略文件
├── services/             # 业务逻辑层（高内聚）
│   ├── __init__.py
│   ├── llm_service.py    # LLM 调用服务
│   └── travel_service.py # 旅行规划服务
└── routes/               # API 路由层（低耦合）
    ├── __init__.py
    └── chat_routes.py    # 聊天相关路由
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backendtest
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的 API Key：

```env
QWEN_API_KEY=your_api_key_here
```

### 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## 📡 API 接口

### 健康检查

```
GET /health
```

### 聊天接口

```
POST /api/chat
```

**请求示例：**

```json
{
  "messages": [
    {"role": "user", "content": "我有两天时间逛北京，该怎么安排？"}
  ]
}
```

**响应示例：**

```json
{
  "response": "详细的行程说明...",
  "locations": [
    {
      "name": "天安门广场",
      "lat": 39.9042,
      "lng": 116.3976,
      "time": "第1天 08:00-10:00",
      "description": "参观天安门广场..."
    }
  ],
  "itinerary_title": "北京两日游"
}
```

### 获取当前行程

```
GET /api/itinerary
```

### 清除当前行程

```
DELETE /api/itinerary
```

## 🎯 架构设计

### 高内聚低耦合原则

1. **配置层** (`config.py`)
   - 集中管理所有配置
   - 支持环境变量覆盖

2. **模型层** (`models.py`)
   - 统一的数据模型定义
   - Pydantic 数据验证

3. **服务层** (`services/`)
   - `llm_service.py`: 封装所有 LLM 相关操作
   - `travel_service.py`: 处理旅行规划业务逻辑
   - 每个服务职责单一，高度内聚

4. **路由层** (`routes/`)
   - 按功能模块划分路由
   - 只负责请求转发和响应格式化
   - 不包含业务逻辑，实现低耦合

### 数据流

```
用户请求 → Router → Service → LLM Service → 返回结果
```

## 🔧 开发指南

### 添加新的 API 端点

1. 在 `routes/` 目录下创建新的路由文件
2. 在 `services/` 目录下实现对应的业务逻辑
3. 在 `main.py` 中注册新路由

### 扩展地点数据库

在 `travel_service.py` 的 `_find_location_to_add` 方法中添加新地点：

```python
location_database = {
    "新地点关键词": {
        "name": "地点名称",
        "lat": 纬度,
        "lng": 经度,
        "time": "时间安排",
        "description": "描述"
    }
}
```

## 📝 注意事项

1. **API Key 安全**: 不要将 `.env` 文件提交到版本控制系统
2. **CORS 配置**: 根据前端实际地址配置 `CORS_ORIGINS`
3. **错误处理**: 所有异常都已捕获并返回友好的错误信息

## 🛠️ 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Pydantic**: 数据验证和设置管理
- **httpx**: 异步 HTTP 客户端
- **Uvicorn**: ASGI 服务器

## 📄 License

MIT
