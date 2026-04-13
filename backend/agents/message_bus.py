"""
消息总线 - 智能体间通信基础设施
实现发布-订阅模式，解耦智能体依赖
"""
import asyncio
from typing import Dict, List, Callable, Awaitable, Optional
from agents.mcp_protocol import MCPMessage, MCPResponse, MessageType
import uuid
import logging

logger = logging.getLogger(__name__)


class MessageBus:
    """
    消息总线 - 智能体通信中枢
    
    功能：
    1. 消息路由：根据接收者将消息分发到对应智能体
    2. 异步通信：支持异步消息处理
    3. 解耦设计：智能体不需要知道彼此的存在
    """
    
    def __init__(self):
        # 注册表：agent_name -> handler function
        self._handlers: Dict[str, Callable[[MCPMessage], Awaitable[MCPResponse]]] = {}
        # 消息历史（用于调试和追踪）
        self._message_history: List[MCPMessage] = []
        # 锁机制保证线程安全
        self._lock = asyncio.Lock()
    
    def register_agent(self, agent_name: str, handler: Callable[[MCPMessage], Awaitable[MCPResponse]]):
        """
        注册智能体处理器
        
        Args:
            agent_name: 智能体名称
            handler: 消息处理函数
        """
        if agent_name in self._handlers:
            logger.warning(f"智能体 {agent_name} 已存在，将被覆盖")
        
        self._handlers[agent_name] = handler
        logger.info(f"✅ 智能体已注册: {agent_name}")
    
    def unregister_agent(self, agent_name: str):
        """注销智能体"""
        if agent_name in self._handlers:
            del self._handlers[agent_name]
            logger.info(f"❌ 智能体已注销: {agent_name}")
    
    async def send_message(self, message: MCPMessage) -> MCPResponse:
        """
        发送消息到指定智能体
        
        Args:
            message: MCP消息对象
            
        Returns:
            MCP响应对象
        """
        async with self._lock:
            # 记录消息历史
            self._message_history.append(message)
            
            # 查找目标智能体
            receiver = message.receiver
            if receiver not in self._handlers:
                error_msg = f"未找到接收者: {receiver}"
                logger.error(error_msg)
                return MCPResponse(
                    success=False,
                    error=error_msg,
                    message_id=message.message_id
                )
            
            try:
                logger.debug(f"📤 发送消息: {message.sender} -> {receiver} [{message.action}]")
                
                # 调用处理器
                handler = self._handlers[receiver]
                response = await handler(message)
                
                # 设置关联的消息ID
                response.message_id = message.message_id
                
                logger.debug(f"📥 收到响应: {response.success}")
                return response
                
            except Exception as e:
                error_msg = f"处理消息失败: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return MCPResponse(
                    success=False,
                    error=error_msg,
                    message_id=message.message_id
                )
    
    async def broadcast(self, message: MCPMessage, exclude: List[str] = None) -> List[MCPResponse]:
        """
        广播消息给所有智能体
        
        Args:
            message: MCP消息对象
            exclude: 排除的智能体列表
            
        Returns:
            所有响应列表
        """
        exclude = exclude or []
        responses = []
        
        for agent_name in self._handlers.keys():
            if agent_name not in exclude:
                # 创建副本并修改接收者
                broadcast_msg = message.copy()
                broadcast_msg.receiver = agent_name
                response = await self.send_message(broadcast_msg)
                responses.append(response)
        
        return responses
    
    def get_registered_agents(self) -> List[str]:
        """获取已注册的智能体列表"""
        return list(self._handlers.keys())
    
    def get_message_history(self, limit: int = 100) -> List[MCPMessage]:
        """获取消息历史"""
        return self._message_history[-limit:]
    
    def clear_history(self):
        """清空消息历史"""
        self._message_history.clear()


# 全局消息总线实例
message_bus = MessageBus()
