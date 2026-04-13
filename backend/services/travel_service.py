"""
旅行规划服务层 - 处理旅行计划相关业务逻辑
"""
from typing import List, Dict, Optional
from models import Location
from services.llm_service import llm_service
from services.geocoding_service import geocoding_service


class TravelService:
    """旅行服务类 - 封装所有旅行规划相关逻辑"""
    
    def __init__(self):
        self.current_itinerary: Optional[Dict] = None
    
    async def process_chat_message(
        self, 
        user_input: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict:
        """
        处理用户聊天消息
        
        Args:
            user_input: 用户输入
            conversation_history: 对话历史
            
        Returns:
            包含 response、locations、itinerary_title 的字典
        """
        # 检查是否是修改现有行程
        if self.current_itinerary and self._is_modification_request(user_input):
            return await self._handle_itinerary_modification(user_input)
        
        # 调用 LLM 生成回复和行程
        result = await llm_service.generate_travel_plan(
            user_input=user_input,
            conversation_history=conversation_history
        )
        
        print(f"\n📊 LLM返回结果检查:")
        print(f"   response 长度: {len(result.get('response', ''))}")
        print(f"   locations 类型: {type(result.get('locations'))}")
        print(f"   locations 值: {result.get('locations')}")
        print(f"   itinerary_title: {result.get('itinerary_title')}")
        
        # 如果返回了地点信息，使用地理编码服务修正坐标
        if result.get("locations") and len(result["locations"]) > 0:
            print(f"\n🔧 开始修正 {len(result['locations'])} 个地点的坐标...")
            
            # 打印原始坐标
            for i, loc in enumerate(result['locations']):
                print(f"   原始 [{i+1}] {loc.get('name')}: ({loc.get('lat')}, {loc.get('lng')})")
            
            result["locations"] = await geocoding_service.batch_geocode(result["locations"])
            
            # 打印修正后的坐标
            print(f"\n✅ 修正后的坐标:")
            for i, loc in enumerate(result['locations']):
                print(f"   修正 [{i+1}] {loc.get('name')}: ({loc.get('lat')}, {loc.get('lng')})")
            
            self.current_itinerary = {
                "title": result.get("itinerary_title", "旅游行程"),
                "locations": result["locations"]
            }
        else:
            print(f"\n⚠️ 没有locations数据，跳过地理编码")
            print(f"   locations 是否为 None: {result.get('locations') is None}")
            print(f"   locations 是否为空列表: {result.get('locations') == []}")
        
        return result
    
    def _is_modification_request(self, user_input: str) -> bool:
        """
        判断用户输入是否是修改行程的请求
        
        Args:
            user_input: 用户输入
            
        Returns:
            是否为修改请求
        """
        modification_keywords = [
            "删除", "去掉", "不去",
            "添加", "加上", "增加",
            "提前", "推迟", "改到",
            "先去", "调换", "换一下"
        ]
        
        return any(keyword in user_input for keyword in modification_keywords)
    
    async def _handle_itinerary_modification(self, user_input: str) -> Dict:
        """
        处理行程修改请求
        
        Args:
            user_input: 用户输入
            
        Returns:
            修改后的行程结果
        """
        if not self.current_itinerary:
            return {
                "response": "当前没有行程可以修改。请先创建一个旅行计划。",
                "locations": [],
                "itinerary_title": None
            }
        
        input_lower = user_input.lower()
        locations = self.current_itinerary["locations"].copy()
        response_text = ""
        
        # 删除景点
        if any(kw in input_lower for kw in ["删除", "去掉", "不去"]):
            location_to_remove = None
            for loc in locations:
                if loc["name"] in user_input or loc["name"].lower() in input_lower:
                    location_to_remove = loc
                    break
            
            if location_to_remove:
                locations = [loc for loc in locations if loc["name"] != location_to_remove["name"]]
                response_text = f"好的，我已经将「{location_to_remove['name']}」从行程中删除了。下面是更新后的行程："
                
                self.current_itinerary["locations"] = locations
                return {
                    "response": response_text,
                    "locations": locations,
                    "itinerary_title": self.current_itinerary["title"]
                }
        
        # 添加景点（简单规则匹配）
        if any(kw in input_lower for kw in ["添加", "加上", "增加"]):
            new_location = self._find_location_to_add(user_input)
            if new_location:
                # 插入到合适的位置（这里简化处理，添加到中间）
                insert_index = min(len(locations), 3)
                locations.insert(insert_index, new_location)
                response_text = f"好的，我已经将「{new_location['name']}」添加到行程中。下面是更新后的行程："
                
                self.current_itinerary["locations"] = locations
                return {
                    "response": response_text,
                    "locations": locations,
                    "itinerary_title": self.current_itinerary["title"]
                }
        
        # 其他修改（时间调整、顺序调整等）- 调用LLM重新生成
        # 这里可以进一步优化，目前先返回提示
        return {
            "response": "我理解您想修改行程。为了更好地满足您的需求，能否详细说明一下您的修改要求？我会为您重新规划。",
            "locations": locations,
            "itinerary_title": self.current_itinerary["title"]
        }
    
    def _find_location_to_add(self, user_input: str) -> Optional[Dict]:
        """
        根据用户输入查找要添加的地点
        
        Args:
            user_input: 用户输入
            
        Returns:
            地点信息字典，如果未找到则返回None
        """
        # 预定义的地点数据库（可以扩展）
        location_database = {
            "鸟巢": {
                "name": "鸟巢/水立方",
                "lat": 39.9928,
                "lng": 116.3903,
                "time": "第2天 09:00-12:00",
                "description": "参观2008年奥运会主场馆，感受现代建筑的魅力"
            },
            "水立方": {
                "name": "鸟巢/水立方",
                "lat": 39.9928,
                "lng": 116.3903,
                "time": "第2天 09:00-12:00",
                "description": "参观2008年奥运会主场馆，感受现代建筑的魅力"
            },
            "天坛": {
                "name": "天坛公园",
                "lat": 39.8828,
                "lng": 116.4068,
                "time": "第1天 16:00-17:30",
                "description": "游览明清两代皇帝祭天的场所，欣赏古代建筑艺术"
            },
            "圆明园": {
                "name": "圆明园",
                "lat": 40.0080,
                "lng": 116.3103,
                "time": "第2天 14:00-17:00",
                "description": "参观皇家园林遗址，了解历史沧桑"
            },
            "雍和宫": {
                "name": "雍和宫",
                "lat": 39.9495,
                "lng": 116.4177,
                "time": "第1天 15:00-16:30",
                "description": "参观藏传佛教寺院，感受宗教文化"
            }
        }
        
        for keyword, location in location_database.items():
            if keyword in user_input:
                return location
        
        return None
    
    def clear_itinerary(self):
        """清除当前行程"""
        self.current_itinerary = None
    
    def get_current_itinerary(self) -> Optional[Dict]:
        """获取当前行程"""
        return self.current_itinerary


# 创建全局旅行服务实例
travel_service = TravelService()
