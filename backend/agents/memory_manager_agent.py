"""
记忆管理智能体 - 负责对话历史和状态持久化
"""
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from agents.mcp_protocol import MCPMessage, MCPResponse
from agents.message_bus import message_bus

logger = logging.getLogger(__name__)


class MemoryManagerAgent:
    """
    记忆管理智能体
    
    职责：
    1. 管理对话历史
    2. 保存和加载行程状态
    3. 上下文管理
    4. 数据持久化
    """
    
    def __init__(self, storage_path: str = "data/memory"):
        self.agent_name = "memory_manager"
        self.storage_path = Path(storage_path)
        
        # 内存中的当前状态
        self.current_itinerary: Optional[Dict] = None
        self.conversation_history: List[Dict] = []
        
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 注册到消息总线
        message_bus.register_agent(self.agent_name, self.handle_message)
        
        # 加载持久化的数据
        self._load_state()
        
        logger.info("💾 记忆管理智能体已初始化")
    
    async def handle_message(self, message: MCPMessage) -> MCPResponse:
        """处理来自其他智能体的消息"""
        try:
            action = message.action
            payload = message.payload
            
            logger.info(f"📨 记忆管理器收到消息: {action}")
            
            if action == "save_itinerary":
                return await self._save_itinerary(payload)
            elif action == "update_itinerary":
                return await self._update_itinerary(payload)
            elif action == "get_itinerary":
                return await self._get_itinerary()
            elif action == "clear_itinerary":
                return await self._clear_itinerary()
            elif action == "add_conversation":
                return await self._add_conversation(payload)
            elif action == "get_conversation_history":
                return await self._get_conversation_history(payload)
            elif action == "clear_history":
                return await self._clear_history()
            elif action == "get_capabilities":
                return await self._get_capabilities()
            else:
                return MCPResponse(
                    success=False,
                    error=f"未知动作: {action}"
                )
                
        except Exception as e:
            logger.error(f"❌ 记忆管理器处理消息失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=str(e),
                message_id=message.message_id
            )
    
    async def _save_itinerary(self, payload: Dict) -> MCPResponse:
        """
        保存行程
        
        Args:
            payload: {
                "title": str,
                "locations": List[Dict]
            }
        """
        title = payload.get("title", "旅游行程")
        locations = payload.get("locations", [])
        
        self.current_itinerary = {
            "title": title,
            "locations": locations
        }
        
        # 持久化到文件
        self._save_state()
        
        logger.info(f"💾 行程已保存: {title}, {len(locations)} 个地点")
        
        return MCPResponse(
            success=True,
            data={"message": "行程已保存"}
        )
    
    async def _update_itinerary(self, payload: Dict) -> MCPResponse:
        """
        更新行程
        
        Args:
            payload: {
                "title": str (可选),
                "locations": List[Dict]
            }
        """
        if not self.current_itinerary:
            return MCPResponse(
                success=False,
                error="没有可更新的行程"
            )
        
        # 更新字段
        if "title" in payload:
            self.current_itinerary["title"] = payload["title"]
        
        if "locations" in payload:
            self.current_itinerary["locations"] = payload["locations"]
        
        # 持久化
        self._save_state()
        
        logger.info(f"🔄 行程已更新")
        
        return MCPResponse(
            success=True,
            data={"message": "行程已更新"}
        )
    
    async def _get_itinerary(self) -> MCPResponse:
        """获取当前行程"""
        if self.current_itinerary:
            return MCPResponse(
                success=True,
                data=self.current_itinerary
            )
        else:
            return MCPResponse(
                success=True,
                data=None
            )
    
    async def _clear_itinerary(self) -> MCPResponse:
        """清除当前行程"""
        self.current_itinerary = None
        self._save_state()
        
        logger.info("🗑️ 行程已清除")
        
        return MCPResponse(
            success=True,
            data={"message": "行程已清除"}
        )
    
    async def _add_conversation(self, payload: Dict) -> MCPResponse:
        """
        添加对话记录
        
        Args:
            payload: {
                "role": str,
                "content": str
            }
        """
        role = payload.get("role", "user")
        content = payload.get("content", "")
        
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        # 限制历史记录长度（保留最近50条）
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        return MCPResponse(
            success=True,
            data={"message": "对话已添加"}
        )
    
    async def _get_conversation_history(self, payload: Dict) -> MCPResponse:
        """
        获取对话历史
        
        Args:
            payload: {
                "limit": int (可选，默认全部)
            }
        """
        limit = payload.get("limit", None)
        
        if limit:
            history = self.conversation_history[-limit:]
        else:
            history = self.conversation_history
        
        return MCPResponse(
            success=True,
            data=history
        )
    
    async def _clear_history(self) -> MCPResponse:
        """清除对话历史"""
        self.conversation_history.clear()
        
        logger.info("🗑️ 对话历史已清除")
        
        return MCPResponse(
            success=True,
            data={"message": "对话历史已清除"}
        )
    
    async def _get_capabilities(self) -> MCPResponse:
        """返回智能体能力描述"""
        return MCPResponse(
            success=True,
            data={
                "agent_name": self.agent_name,
                "capabilities": ["state_management", "persistence", "context_tracking"],
                "actions": [
                    "save_itinerary", "update_itinerary", "get_itinerary", 
                    "clear_itinerary", "add_conversation", 
                    "get_conversation_history", "clear_history", "get_capabilities"
                ]
            }
        )
    
    def _save_state(self):
        """将状态保存到文件"""
        try:
            state_file = self.storage_path / "current_state.json"
            state_data = {
                "current_itinerary": self.current_itinerary,
                "conversation_history": self.conversation_history
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            logger.debug("💾 状态已持久化")
            
        except Exception as e:
            logger.error(f"保存状态失败: {e}")
    
    def _load_state(self):
        """从文件加载状态"""
        try:
            state_file = self.storage_path / "current_state.json"
            
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                self.current_itinerary = state_data.get("current_itinerary")
                self.conversation_history = state_data.get("conversation_history", [])
                
                logger.info("✅ 状态已从文件加载")
            else:
                logger.info("📄 未找到状态文件，使用空状态")
                
        except Exception as e:
            logger.error(f"加载状态失败: {e}")


# 全局记忆管理智能体实例
memory_manager_agent = MemoryManagerAgent()
