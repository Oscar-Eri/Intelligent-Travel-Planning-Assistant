# 旅行地图 - 智能旅游规划助手

一个基于 AI 的智能旅游规划应用，帮助你轻松规划完美旅程。

## ✨ 功能特性

- 🗺️ **智能行程规划**：根据目的地和时间自动生成详细行程
- 📍 **地图可视化**：在地图上直观展示旅行路线和景点
- 💬 **自然对话**：通过对话方式与 AI 助手交流
- ✏️ **灵活修改**：支持添加、删除、调整景点
- 🎯 **精准推荐**：基于地理位置和时间的智能推荐

## 📁 项目结构

```
旅行地图/
├── backend/                 # 后端服务（FastAPI）
│   ├── config.py           # 配置管理
│   ├── models.py           # 数据模型
│   ├── main.py             # 应用入口
│   ├── services/           # 业务逻辑层
│   │   ├── llm_service.py      # LLM 调用服务
│   │   └── travel_service.py   # 旅行规划服务
│   ├── routes/             # API 路由层
│   │   └── chat_routes.py      # 聊天相关路由
│   ├── requirements.txt    # Python 依赖
│   ├── .env                # 环境变量配置
│   ├── test_api.py         # API 测试脚本
│   ├── 启动服务.bat        # Windows 启动脚本
│   └── README.md           # 后端详细说明
│
├── frontend/               # 前端应用（React + Vite）
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   └── TravelMap.tsx  # 地图组件
│   │   │   └── App.tsx            # 主应用
│   │   └── styles/         # 样式文件
│   ├── package.json        # Node.js 依赖
│   └── vite.config.ts      # Vite 配置
│
├── config.py               # 全局配置
├── FRONTEND_INTEGRATION.md # 前后端集成指南
└── README.md               # 本文件
```

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- npm 或 pnpm

### 1. 后端设置

```bash
# 进入后端目录
cd backendtest

# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量（编辑 .env 文件）
# 确保 QWEN_API_KEY 已正确配置

# 启动后端服务
python main.py
# 或者在 Windows 上双击：启动服务.bat
```

后端将在 `http://localhost:8000` 运行。

### 2. 前端设置

```bash
# 进入前端目录
cd frontendtest

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 运行。

### 3. 访问应用

打开浏览器访问：`http://localhost:5173`

## 📡 API 接口

### 聊天接口

**POST** `/api/chat`

请求体：
```json
{
  "messages": [
    {"role": "user", "content": "我有两天时间逛北京，该怎么安排？"}
  ]
}
```

响应：
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

**GET** `/api/itinerary`

### 清除当前行程

**DELETE** `/api/itinerary`

### 健康检查

**GET** `/health`

查看完整 API 文档：`http://localhost:8000/docs`

## 🧪 测试

### 后端 API 测试

```bash
cd backendtest
pip install requests
python test_api.py
```

## 🎯 使用示例

### 创建新行程

```
用户：我有两天时间逛北京，该怎么安排？

AI：返回详细的北京两日游行程，包括：
- 天安门广场
- 故宫博物院
- 八达岭长城
- 颐和园
...等景点
```

### 修改行程

```
用户：删除故宫博物院

AI：好的，我已经将「故宫博物院」从行程中删除了。

用户：添加天坛

AI：好的，我已经将「天坛公园」添加到行程中。
```

## 🛠️ 技术栈

### 后端
- **FastAPI** - 现代、快速的 Web 框架
- **Pydantic** - 数据验证
- **httpx** - 异步 HTTP 客户端
- **通义千问 API** - AI 语言模型

### 前端
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **pigeon-maps** - 地图组件
- **lucide-react** - 图标库

## 📝 开发指南

### 架构设计原则

1. **高内聚低耦合**
   - 服务层封装业务逻辑
   - 路由层只负责请求转发
   - 各模块职责清晰

2. **分层架构**
   ```
   用户请求 → Router → Service → LLM Service → 返回结果
   ```

3. **可扩展性**
   - 易于添加新的 API 端点
   - 易于扩展地点数据库
   - 易于集成新的 AI 模型

### 添加新功能

1. **添加新的 API 端点**
   - 在 `backend/routes/` 创建新路由文件
   - 在 `backend/services/` 实现业务逻辑
   - 在 `backend/main.py` 注册路由

2. **扩展地点数据库**
   - 编辑 `backend/services/travel_service.py`
   - 在 `_find_location_to_add` 方法中添加新地点

3. **修改前端**
   - 编辑 `frontend/src/app/App.tsx`
   - 更新组件和样式

## ⚙️ 配置说明

### 环境变量

在 `backend/.env` 中配置：

```env
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 通义千问 API
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=your_api_key_here
QWEN_MODEL=qwen-plus

# CORS 配置
CORS_ORIGINS=["http://localhost:5173", "*"]
```

## 🔒 安全注意事项

1. **保护 API Key**
   - 不要将 `.env` 文件提交到版本控制
   - 使用环境变量管理敏感信息

2. **CORS 配置**
   - 生产环境限制允许的域名
   - 不要使用 `*` 通配符

3. **输入验证**
   - 所有用户输入都经过 Pydantic 验证
   - 防止注入攻击

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题，请提交 Issue。

---

**祝你旅途愉快！** 🌍✈️
