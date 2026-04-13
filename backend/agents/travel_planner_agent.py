"""
旅行规划智能体 - 专注于行程生成和优化
"""
import json
import logging
from typing import Dict, List, Optional
from agents.mcp_protocol import MCPMessage, MCPResponse, MessageType
from agents.message_bus import message_bus
from services.llm_service import llm_service

logger = logging.getLogger(__name__)


class TravelPlannerAgent:
    """
    旅行规划智能体
    
    职责：
    1. 根据用户需求生成旅行计划
    2. 景点推荐和时间安排
    3. 行程修改和优化
    """
    
    def __init__(self):
        self.agent_name = "travel_planner"
        
        # 注册到消息总线
        message_bus.register_agent(self.agent_name, self.handle_message)
        
        logger.info("✈️ 旅行规划智能体已初始化")
    
    async def handle_message(self, message: MCPMessage) -> MCPResponse:
        """处理来自协调者或其他智能体的消息"""
        try:
            action = message.action
            payload = message.payload
            
            logger.info(f"📨 旅行规划者收到消息: {action}")
            
            if action == "generate_plan":
                return await self._generate_plan(payload)
            elif action == "modify_plan":
                return await self._modify_plan(payload)
            elif action == "get_capabilities":
                return await self._get_capabilities()
            else:
                return MCPResponse(
                    success=False,
                    error=f"未知动作: {action}"
                )
                
        except Exception as e:
            logger.error(f"❌ 旅行规划者处理消息失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=str(e),
                message_id=message.message_id
            )
    
    async def _generate_plan(self, payload: Dict) -> MCPResponse:
        """
        生成旅行计划
        
        Args:
            payload: {
                "user_input": str,
                "conversation_history": List[Dict]
            }
        """
        user_input = payload.get("user_input", "")
        conversation_history = payload.get("conversation_history", [])
        
        logger.info(f"📝 生成旅行计划: {user_input[:50]}...")
        
        try:
            result = await llm_service.generate_travel_plan(
                user_input=user_input,
                conversation_history=conversation_history
            )
            
            logger.info(f"✅ 旅行计划生成成功")
            logger.info(f"   标题: {result.get('itinerary_title')}")
            logger.info(f"   地点数: {len(result.get('locations', []))}")
            
            return MCPResponse(
                success=True,
                data=result
            )
            
        except Exception as e:
            logger.error(f"❌ 生成旅行计划失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=f"生成旅行计划失败: {str(e)}"
            )
    
    async def _modify_plan(self, payload: Dict) -> MCPResponse:
        """
        修改现有旅行计划
        
        Args:
            payload: {
                "user_input": str,
                "current_itinerary": Dict
            }
        """
        user_input = payload.get("user_input", "")
        current_itinerary = payload.get("current_itinerary", {})
        
        if not current_itinerary:
            return MCPResponse(
                success=False,
                error="没有可修改的行程"
            )
        
        logger.info(f"🔧 修改旅行计划: {user_input[:50]}...")
        
        try:
            # 构建修改请求的系统提示
            system_prompt = f"""你是一个旅行计划修改助手。当前有一个现有行程，用户想要修改它。

当前行程：
标题: {current_itinerary.get('title', '未命名')}
地点列表:
{json.dumps(current_itinerary.get('locations', []), ensure_ascii=False, indent=2)}

用户的修改要求：{user_input}

请根据用户的要求修改行程，并返回更新后的完整行程JSON格式：
{{
  "title": "行程标题",
  "response": "修改说明和更新后的行程介绍",
  "locations": [...]
}}

注意：
- 只返回JSON，不要其他文字
- locations必须包含所有保留的地点
- 保持JSON格式有效"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            response_text = ""
            async for chunk in llm_service.chat_completion(messages, stream=False):
                response_text += chunk
            
            # 解析JSON
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end]
                    modified_data = json.loads(json_str)
                    
                    return MCPResponse(
                        success=True,
                        data={
                            "response": modified_data.get("response", ""),
                            "locations": modified_data.get("locations", []),
                            "itinerary_title": modified_data.get("title", current_itinerary.get("title"))
                        }
                    )
                else:
                    return MCPResponse(
                        success=False,
                        error="无法解析修改后的行程JSON"
                    )
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                return MCPResponse(
                    success=False,
                    error=f"JSON解析失败: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"❌ 修改旅行计划失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=f"修改旅行计划失败: {str(e)}"
            )
    
    async def _get_capabilities(self) -> MCPResponse:
        """返回智能体能力描述"""
        return MCPResponse(
            success=True,
            data={
                "agent_name": self.agent_name,
                "capabilities": ["plan_generation", "plan_modification", "recommendation"],
                "actions": ["generate_plan", "modify_plan", "get_capabilities"]
            }
        )


# 全局旅行规划智能体实例
travel_planner_agent = TravelPlannerAgent()
