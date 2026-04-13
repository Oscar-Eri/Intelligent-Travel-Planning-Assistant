"""
协调者智能体 - 系统的大脑
负责理解用户意图、任务分解和结果整合
"""
import uuid
import json
import logging
from typing import Dict, List, Optional, Any
from agents.mcp_protocol import MCPMessage, MCPResponse, MessageType, MessagePriority
from agents.message_bus import message_bus
from services.llm_service import llm_service

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    协调者智能体
    
    职责：
    1. 理解用户意图（闲聊 vs 旅行规划）
    2. 任务分解与路由
    3. 多智能体协作调度
    4. 结果整合与返回
    """
    
    def __init__(self):
        self.agent_name = "coordinator"
        self.current_context: Dict[str, Any] = {}
        
        # 注册到消息总线
        message_bus.register_agent(self.agent_name, self.handle_message)
        
        logger.info("🧠 协调者智能体已初始化")
    
    async def handle_message(self, message: MCPMessage) -> MCPResponse:
        """处理来自其他智能体或外部的消息"""
        try:
            action = message.action
            payload = message.payload
            
            logger.info(f"📨 协调者收到消息: {action}")
            
            if action == "process_user_input":
                return await self._process_user_input(payload)
            elif action == "get_capabilities":
                return await self._get_capabilities()
            else:
                return MCPResponse(
                    success=False,
                    error=f"未知动作: {action}"
                )
                
        except Exception as e:
            logger.error(f"❌ 协调者处理消息失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=str(e),
                message_id=message.message_id
            )
    
    async def _process_user_input(self, payload: Dict) -> MCPResponse:
        """
        处理用户输入
        
        流程：
        1. 分析意图
        2. 调用相应智能体
        3. 整合结果
        """
        user_input = payload.get("user_input", "")
        conversation_history = payload.get("conversation_history", [])
        
        logger.info(f"💬 处理用户输入: {user_input[:50]}...")
        
        # Step 1: 意图识别
        intent = await self._analyze_intent(user_input, conversation_history)
        logger.info(f"🎯 识别意图: {intent}")
        
        # Step 2: 根据意图路由
        if intent == "chat":
            # 闲聊模式，直接调用LLM
            response_text = await self._handle_chat(user_input, conversation_history)
            return MCPResponse(
                success=True,
                data={
                    "response": response_text,
                    "locations": [],
                    "itinerary_title": None,
                    "intent": intent
                }
            )
        
        elif intent == "travel_planning":
            # 旅行规划模式，调用多个智能体协作
            return await self._handle_travel_planning(user_input, conversation_history)
        
        elif intent == "itinerary_modification":
            # 行程修改模式
            return await self._handle_itinerary_modification(user_input, conversation_history)
        
        else:
            # 默认按旅行规划处理
            return await self._handle_travel_planning(user_input, conversation_history)
    
    async def _analyze_intent(self, user_input: str, history: List[Dict]) -> str:
        """
        分析用户意图
        
        Returns:
            "chat" | "travel_planning" | "itinerary_modification"
        """
        # 检查是否有当前行程
        has_current_itinerary = bool(self.current_context.get("current_itinerary"))
        
        # 修改请求关键词
        modification_keywords = ["删除", "去掉", "不去", "添加", "加上", "增加", 
                               "提前", "推迟", "改到", "先去", "调换", "换一下"]
        
        if any(kw in user_input for kw in modification_keywords) and has_current_itinerary:
            return "itinerary_modification"
        
        # 使用LLM进行更精确的意图识别
        system_prompt = """你是一个意图识别助手。判断用户输入的意图类型：

1. "chat" - 闲聊、问候、一般性问题（如：你好、谢谢、你是谁）
2. "travel_planning" - 旅行规划相关（如：推荐景点、安排行程、XX地怎么玩）
3. "itinerary_modification" - 修改现有行程（如：删除某个景点、调整时间）

只返回一个词：chat 或 travel_planning 或 itinerary_modification"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户输入: {user_input}"}
        ]
        
        try:
            intent_result = ""
            async for chunk in llm_service.chat_completion(messages, stream=False):
                intent_result += chunk
            
            intent_result = intent_result.strip().lower()
            
            if "chat" in intent_result:
                return "chat"
            elif "modification" in intent_result:
                return "itinerary_modification"
            else:
                return "travel_planning"
                
        except Exception as e:
            logger.warning(f"意图识别失败，使用规则匹配: {e}")
            # 降级：基于关键词判断
            travel_keywords = ["旅游", "旅行", "景点", "行程", "玩", "逛", "安排", "推荐"]
            if any(kw in user_input for kw in travel_keywords):
                return "travel_planning"
            return "chat"
    
    async def _handle_chat(self, user_input: str, history: List[Dict]) -> str:
        """处理闲聊"""
        messages = [
            {"role": "system", "content": "你是一个友好的旅行助手，可以进行日常对话。"},
        ]
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_input})
        
        response_text = ""
        async for chunk in llm_service.chat_completion(messages, stream=False):
            response_text += chunk
        
        return response_text
    
    async def _handle_travel_planning(self, user_input: str, history: List[Dict]) -> MCPResponse:
        """
        处理旅行规划请求
        
        多智能体协作流程：
        1. TravelPlannerAgent - 生成初步行程
        2. GeoCoderAgent - 修正地理坐标
        3. MemoryManagerAgent - 保存上下文
        4. Coordinator - 整合结果
        """
        logger.info("🚀 启动旅行规划多智能体协作流程")
        
        # Step 1: 调用旅行规划智能体
        planning_response = await message_bus.send_message(MCPMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.REQUEST,
            sender=self.agent_name,
            receiver="travel_planner",
            action="generate_plan",
            payload={
                "user_input": user_input,
                "conversation_history": history
            },
            priority=MessagePriority.HIGH
        ))
        
        if not planning_response.success:
            logger.error(f"旅行规划失败: {planning_response.error}")
            return MCPResponse(
                success=False,
                error=f"旅行规划失败: {planning_response.error}"
            )
        
        plan_data = planning_response.data
        locations = plan_data.get("locations", [])
        
        # Step 2: 如果有地点，调用地理编码智能体修正坐标
        if locations and len(locations) > 0:
            logger.info(f"🗺️ 调用地理编码智能体修正 {len(locations)} 个地点")
            
            geocoding_response = await message_bus.send_message(MCPMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.REQUEST,
                sender=self.agent_name,
                receiver="geo_coder",
                action="batch_geocode",
                payload={"locations": locations},
                priority=MessagePriority.NORMAL
            ))
            
            if geocoding_response.success:
                locations = geocoding_response.data
                plan_data["locations"] = locations
                logger.info("✅ 地理编码完成")
            else:
                logger.warning(f"⚠️ 地理编码失败，使用原始坐标: {geocoding_response.error}")
        
        # Step 3: 保存到记忆管理器
        memory_response = await message_bus.send_message(MCPMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.REQUEST,
            sender=self.agent_name,
            receiver="memory_manager",
            action="save_itinerary",
            payload={
                "title": plan_data.get("itinerary_title", "旅游行程"),
                "locations": locations
            },
            priority=MessagePriority.LOW
        ))
        
        if memory_response.success:
            logger.info("💾 行程已保存到记忆")
            self.current_context["current_itinerary"] = {
                "title": plan_data.get("itinerary_title"),
                "locations": locations
            }
        
        # Step 4: 返回整合结果
        return MCPResponse(
            success=True,
            data={
                "response": plan_data.get("response", ""),
                "locations": locations,
                "itinerary_title": plan_data.get("itinerary_title"),
                "intent": "travel_planning"
            }
        )
    
    async def _handle_itinerary_modification(self, user_input: str, history: List[Dict]) -> MCPResponse:
        """处理行程修改请求"""
        current_itinerary = self.current_context.get("current_itinerary")
        
        if not current_itinerary:
            return MCPResponse(
                success=False,
                error="当前没有行程可以修改"
            )
        
        # 委托给旅行规划智能体处理修改
        modification_response = await message_bus.send_message(MCPMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.REQUEST,
            sender=self.agent_name,
            receiver="travel_planner",
            action="modify_plan",
            payload={
                "user_input": user_input,
                "current_itinerary": current_itinerary
            },
            priority=MessagePriority.HIGH
        ))
        
        if modification_response.success:
            modified_data = modification_response.data
            # 更新记忆
            await message_bus.send_message(MCPMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.REQUEST,
                sender=self.agent_name,
                receiver="memory_manager",
                action="update_itinerary",
                payload=modified_data
            ))
            
            self.current_context["current_itinerary"] = {
                "title": modified_data.get("itinerary_title"),
                "locations": modified_data.get("locations", [])
            }
        
        return modification_response
    
    async def _get_capabilities(self) -> MCPResponse:
        """返回智能体能力描述"""
        return MCPResponse(
            success=True,
            data={
                "agent_name": self.agent_name,
                "capabilities": ["intent_analysis", "task_routing", "result_integration"],
                "actions": ["process_user_input", "get_capabilities"]
            }
        )
    
    def get_current_itinerary(self) -> Optional[Dict]:
        """获取当前行程"""
        return self.current_context.get("current_itinerary")
    
    def clear_context(self):
        """清空上下文"""
        self.current_context.clear()


# 全局协调者智能体实例
coordinator_agent = CoordinatorAgent()
