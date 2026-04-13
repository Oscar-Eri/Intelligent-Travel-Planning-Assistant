"""
聊天相关API路由 - 基于多智能体架构
"""
import uuid
from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse, Location
from agents.mcp_protocol import MCPMessage, MessageType, MessagePriority
from agents.message_bus import message_bus
from agents.coordinator_agent import coordinator_agent

router = APIRouter(
    prefix="/api",
    tags=["chat"]
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口 - 多智能体协作处理
    
    流程：
    1. 接收用户消息
    2. 发送给协调者智能体
    3. 协调者分解任务并调度其他智能体
    4. 整合结果返回
    
    请求示例:
    POST /api/chat
    {
        "messages": [
            {"role": "user", "content": "我有两天时间逛北京，该怎么安排？"}
        ]
    }
    
    响应:
    {
        "response": "详细的行程说明...",
        "locations": [...],
        "itinerary_title": "北京两日游"
    }
    """
    try:
        # 获取最后一条用户消息
        if not request.messages:
            raise HTTPException(status_code=400, detail="消息列表不能为空")
        
        user_message = request.messages[-1]
        if user_message.role != "user":
            raise HTTPException(status_code=400, detail="最后一条消息必须是用户消息")
        
        # 构建对话历史（排除系统消息）
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages[:-1]
        ]
        
        # 创建MCP消息发送给协调者智能体
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
        
        # 通过消息总线发送
        response = await message_bus.send_message(mcp_message)
        
        if not response.success:
            raise HTTPException(
                status_code=500, 
                detail=f"智能体处理失败: {response.error}"
            )
        
        result = response.data
        
        # 转换地点数据
        locations = None
        if result.get("locations") and len(result["locations"]) > 0:
            locations = [
                Location(**loc) if isinstance(loc, dict) else loc
                for loc in result["locations"]
            ]
        
        return ChatResponse(
            response=result["response"],
            locations=locations,
            itinerary_title=result.get("itinerary_title")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理消息失败: {str(e)}")


@router.get("/itinerary")
async def get_current_itinerary():
    """
    获取当前行程 - 从记忆管理智能体获取
    
    返回:
    {
        "title": "行程标题",
        "locations": [...]
    }
    """
    try:
        itinerary = coordinator_agent.get_current_itinerary()
        if itinerary:
            return itinerary
        else:
            return {"title": None, "locations": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行程失败: {str(e)}")


@router.delete("/itinerary")
async def clear_itinerary():
    """
    清除当前行程 - 通知记忆管理智能体
    
    返回:
    {
        "message": "行程已清除"
    }
    """
    try:
        coordinator_agent.clear_context()
        return {"message": "行程已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除行程失败: {str(e)}")
