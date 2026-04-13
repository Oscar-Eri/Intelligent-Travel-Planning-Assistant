"""
旅行地图后端主程序 - 多智能体协作架构
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models import HealthResponse
from routes import chat_routes

# 导入并初始化所有智能体（自动注册到消息总线）
from agents.coordinator_agent import coordinator_agent
from agents.travel_planner_agent import travel_planner_agent
from agents.geo_coder_agent import geo_coder_agent
from agents.memory_manager_agent import memory_manager_agent
from agents.message_bus import message_bus


# 创建 FastAPI 应用
app = FastAPI(
    title="旅行地图AI助手",
    description="智能旅游规划助手 - 帮你规划完美旅程",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_routes.router)


# ============ 启动时初始化 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化所有智能体"""
    print("\n" + "=" * 60)
    print("🤖 多智能体系统初始化中...")
    print("=" * 60)
    
    # 显示已注册的智能体
    registered_agents = message_bus.get_registered_agents()
    print(f"✅ 已注册 {len(registered_agents)} 个智能体:")
    for agent_name in registered_agents:
        print(f"   - {agent_name}")
    
    print("=" * 60)
    print("🚀 系统就绪！\n")


# ============ 基础路由 ============

@app.get("/", response_model=HealthResponse)
async def root():
    """根路径 - 健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "旅行地图AI助手（多智能体版）"
    }


@app.get("/agents/status")
async def get_agents_status():
    """获取所有智能体状态"""
    return {
        "registered_agents": message_bus.get_registered_agents(),
        "message_history_count": len(message_bus.get_message_history())
    }


@app.get("/agents/status")
async def get_agents_status():
    """获取所有智能体状态"""
    return {
        "registered_agents": message_bus.get_registered_agents(),
        "message_history_count": len(message_bus.get_message_history())
    }


# ============ 启动服务 ============

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 旅行地图AI助手启动中...")
    print("=" * 60)
    print(f"📡 服务地址：http://{settings.HOST}:{settings.PORT}")
    print(f"🌐 API 文档：http://{settings.HOST}:{settings.PORT}/docs")
    print(f"💬 聊天接口：http://{settings.HOST}:{settings.PORT}/api/chat")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
