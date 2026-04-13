"""
地理编码智能体 - 专注于地点坐标的精确化
"""
import logging
from typing import Dict, List
from agents.mcp_protocol import MCPMessage, MCPResponse
from agents.message_bus import message_bus
from services.geocoding_service import geocoding_service

logger = logging.getLogger(__name__)


class GeoCoderAgent:
    """
    地理编码智能体
    
    职责：
    1. 将地点名称转换为精确坐标
    2. POI搜索和匹配
    3. 批量地理编码处理
    """
    
    def __init__(self):
        self.agent_name = "geo_coder"
        
        # 注册到消息总线
        message_bus.register_agent(self.agent_name, self.handle_message)
        
        logger.info("🗺️ 地理编码智能体已初始化")
    
    async def handle_message(self, message: MCPMessage) -> MCPResponse:
        """处理来自其他智能体的消息"""
        try:
            action = message.action
            payload = message.payload
            
            logger.info(f"📨 地理编码器收到消息: {action}")
            
            if action == "batch_geocode":
                return await self._batch_geocode(payload)
            elif action == "single_geocode":
                return await self._single_geocode(payload)
            elif action == "poi_search":
                return await self._poi_search(payload)
            elif action == "get_capabilities":
                return await self._get_capabilities()
            else:
                return MCPResponse(
                    success=False,
                    error=f"未知动作: {action}"
                )
                
        except Exception as e:
            logger.error(f"❌ 地理编码器处理消息失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=str(e),
                message_id=message.message_id
            )
    
    async def _batch_geocode(self, payload: Dict) -> MCPResponse:
        """
        批量地理编码
        
        Args:
            payload: {
                "locations": List[Dict]
            }
        """
        locations = payload.get("locations", [])
        
        if not locations:
            return MCPResponse(
                success=True,
                data=[]
            )
        
        logger.info(f"📍 开始批量地理编码，共 {len(locations)} 个地点")
        
        try:
            # 调用地理编码服务
            updated_locations = await geocoding_service.batch_geocode(locations)
            
            logger.info(f"✅ 批量地理编码完成")
            
            return MCPResponse(
                success=True,
                data=updated_locations
            )
            
        except Exception as e:
            logger.error(f"❌ 批量地理编码失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=f"批量地理编码失败: {str(e)}"
            )
    
    async def _single_geocode(self, payload: Dict) -> MCPResponse:
        """
        单个地点地理编码
        
        Args:
            payload: {
                "address": str,
                "city": str (可选)
            }
        """
        address = payload.get("address", "")
        city = payload.get("city", "烟台")
        
        if not address:
            return MCPResponse(
                success=False,
                error="地址不能为空"
            )
        
        logger.info(f"📍 地理编码: {address}")
        
        try:
            coords = await geocoding_service.geocode(address, city)
            
            if coords:
                return MCPResponse(
                    success=True,
                    data=coords
                )
            else:
                return MCPResponse(
                    success=False,
                    error=f"未找到地点: {address}"
                )
                
        except Exception as e:
            logger.error(f"❌ 地理编码失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=f"地理编码失败: {str(e)}"
            )
    
    async def _poi_search(self, payload: Dict) -> MCPResponse:
        """
        POI搜索
        
        Args:
            payload: {
                "keyword": str,
                "city": str,
                "address_hint": str (可选)
            }
        """
        keyword = payload.get("keyword", "")
        city = payload.get("city", "烟台")
        address_hint = payload.get("address_hint", "")
        
        if not keyword:
            return MCPResponse(
                success=False,
                error="关键词不能为空"
            )
        
        logger.info(f"🔍 POI搜索: {keyword} in {city}")
        
        try:
            result = await geocoding_service.poi_search(keyword, city, address_hint)
            
            if result:
                return MCPResponse(
                    success=True,
                    data=result
                )
            else:
                return MCPResponse(
                    success=False,
                    error=f"未找到POI: {keyword}"
                )
                
        except Exception as e:
            logger.error(f"❌ POI搜索失败: {e}", exc_info=True)
            return MCPResponse(
                success=False,
                error=f"POI搜索失败: {str(e)}"
            )
    
    async def _get_capabilities(self) -> MCPResponse:
        """返回智能体能力描述"""
        return MCPResponse(
            success=True,
            data={
                "agent_name": self.agent_name,
                "capabilities": ["geocoding", "poi_search", "batch_processing"],
                "actions": ["batch_geocode", "single_geocode", "poi_search", "get_capabilities"]
            }
        )


# 全局地理编码智能体实例
geo_coder_agent = GeoCoderAgent()
