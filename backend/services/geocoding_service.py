"""
地理编码服务 - 将地点名称转换为准确的经纬度坐标
使用高德地图API
"""
import httpx
from typing import Optional, Dict, List
from config import settings


class GeocodingService:
    """地理编码服务类"""
    
    def __init__(self):
        # 高德地图API配置
        self.amap_key = settings.AMAP_API_KEY
        print(f"🔑 高德地图 API Key: {self.amap_key[:8]}...{self.amap_key[-8:] if len(self.amap_key) > 16 else ''}")
        
        # 如果需要使用Nginx代理，取消下面注释并修改为你的代理地址
        # self.base_url = "http://127.0.0.1/_AMapService"  
        # 否则直接使用高德官方API
        self.base_url = "https://restapi.amap.com"
        self.geocode_url = f"{self.base_url}/v3/geocode/geo"
        self.regeocode_url = f"{self.base_url}/v3/geocode/regeo"
        self.poi_search_url = f"{self.base_url}/v3/place/text"  # POI搜索API
        
        if not self.amap_key:
            print("⚠️ 警告: 未配置高德地图API Key，地理编码功能将不可用")
        else:
            print("✅ 高德地图API Key已配置")
    
    async def geocode(self, address: str, city: str = "烟台") -> Optional[Dict[str, float]]:
        """
        地理编码：将地址转换为经纬度
        
        Args:
            address: 地址字符串
            city: 城市名称（可选，用于提高准确度）
            
        Returns:
            包含 lat 和 lng 的字典，失败返回 None
        """
        if not self.amap_key:
            print("⚠️ 未配置高德地图API Key，跳过地理编码")
            return None
        
        try:
            params = {
                "key": self.amap_key,
                "address": f"{city}{address}" if city else address,
                "output": "json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.geocode_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1" and data.get("count") != "0":
                    # 取第一个结果（最匹配）
                    location_str = data["geocodes"][0]["location"]
                    lng, lat = location_str.split(",")
                    
                    result = {
                        "lat": float(lat),
                        "lng": float(lng)
                    }
                    
                    print(f"✅ 地理编码成功: {address} -> {result}")
                    return result
                else:
                    print(f"⚠️ 地理编码未找到结果: {address}")
                    return None
                    
        except Exception as e:
            print(f"❌ 地理编码失败: {address}, 错误: {e}")
            return None
    
    async def poi_search(self, keyword: str, city: str = "烟台", address_hint: str = "") -> Optional[Dict]:
        """
        POI搜索：搜索地点获取详细信息（比地理编码更准确）
        
        Args:
            keyword: 搜索关键词（地点名称）
            city: 城市名称
            address_hint: 地址提示（从description中提取的详细地址）
            
        Returns:
            包含 name, lat, lng, address 的字典，失败返回 None
        """
        if not self.amap_key:
            print("⚠️ 未配置高德地图API Key，跳过POI搜索")
            return None
        
        try:
            # 构建更精确的搜索关键词
            if address_hint:
                search_keywords = f"{address_hint} {keyword}"
            else:
                search_keywords = keyword
            
            params = {
                "key": self.amap_key,
                "keywords": search_keywords,
                "city": city,
                "citylimit": "true",
                "output": "json",
                "pagesize": 3
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.poi_search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "1" and int(data.get("count", 0)) > 0:
                    pois = data["pois"]
                    best_poi = self._select_best_poi(pois, keyword, address_hint)
                    
                    if best_poi:
                        location_str = best_poi["location"]
                        lng, lat = location_str.split(",")
                        
                        result = {
                            "name": best_poi.get("name", keyword),
                            "lat": float(lat),
                            "lng": float(lng),
                            "address": best_poi.get("address", ""),
                            "type": best_poi.get("typename", "")
                        }
                        
                        print(f"✅ POI搜索成功: {keyword}")
                        print(f"   坐标: ({lat}, {lng})")
                        print(f"   地址: {result['address']}")
                        print(f"   类型: {result['type']}")
                        return result
                    else:
                        print(f"⚠️ POI搜索未找到匹配结果: {keyword}")
                        return None
                else:
                    print(f"⚠️ POI搜索未找到结果: {keyword}")
                    return None
                    
        except Exception as e:
            print(f"❌ POI搜索失败: {keyword}, 错误: {e}")
            return None
    
    def _select_best_poi(self, pois: list, keyword: str, address_hint: str = "") -> Optional[Dict]:
        """从多个POI结果中选择最匹配的一个"""
        if not pois:
            return None
        
        if len(pois) == 1:
            return pois[0]
        
        best_score = -1
        best_poi = None
        
        for poi in pois:
            score = 0
            poi_name = poi.get("name", "")
            poi_address = poi.get("address", "")
            
            # 1. 名称匹配度
            if keyword in poi_name:
                score += 10
            elif poi_name in keyword:
                score += 8
            
            # 2. 地址匹配度
            if address_hint and address_hint in poi_address:
                score += 5
            
            # 3. 类型匹配度（优先选择景点、公园等）
            poi_type = poi.get("typename", "")
            if any(t in poi_type for t in ["风景名胜", "公园", "景点", "广场"]):
                score += 3
            elif any(t in poi_type for t in ["餐厅", "购物", "酒店"]):
                score -= 2
            
            # 4. 排除不相关的商业场所
            if any(exclude in poi_name for exclude in ["旺角", "小渔村", "餐馆", "饭店"]):
                if "码头" in keyword or "广场" in keyword:
                    score -= 10
            
            if score > best_score:
                best_score = score
                best_poi = poi
        
        return best_poi
    
    async def batch_geocode(self, locations: List[Dict]) -> List[Dict]:
        """
        批量地理编码（优先使用POI搜索，更准确）
        
        Args:
            locations: 地点列表，每个地点包含 name 字段
            
        Returns:
            更新后的地点列表，包含准确的 lat 和 lng
        """
        if not self.amap_key:
            print("⚠️ 未配置高德地图API Key，跳过批量地理编码")
            return locations
        
        print(f"\n🗺️ 开始批量地理编码，共 {len(locations)} 个地点...")
        
        updated_locations = []
        for loc in locations:
            # 提取城市信息（从地点名称或描述中）
            name = loc.get("name", "")
            description = loc.get("description", "")
            
            # 尝试从名称中提取城市和区县
            city = self._extract_city(name, description)
            district = self._extract_district(name, description, city)
            
            # 构建搜索关键词：城市 + 区县 + 地点名
            if district and district != city:
                search_keyword = f"{district}{name}"
            else:
                search_keyword = name
            
            print(f"   📍 搜索: {search_keyword} (城市: {city})")
            
            # 从 description 中提取地址提示（“位于...”之后的内容）
            address_hint = ""
            if "位于" in description:
                # 提取“位于”后面的地址信息
                start_idx = description.find("位于") + 2
                end_idx = description.find("。", start_idx)
                if end_idx == -1:
                    end_idx = description.find(",", start_idx)
                if end_idx != -1:
                    address_hint = description[start_idx:end_idx].strip()
            
            # 优先使用POI搜索（更准确）
            poi_result = await self.poi_search(search_keyword, city, address_hint)
            
            if poi_result:
                # 使用POI搜索结果
                loc["name"] = poi_result["name"]  # 使用高德返回的官方名称
                loc["lat"] = poi_result["lat"]
                loc["lng"] = poi_result["lng"]
                
                # 如果description中没有地址，使用POI返回的地址
                if "位于" not in description and poi_result["address"]:
                    loc["description"] = f"位于{poi_result['address']}。{description}"
                
                print(f"   ✅ {loc['name']}: ({poi_result['lat']}, {poi_result['lng']})")
            else:
                # POI搜索失败，降级使用地理编码
                print(f"   ⚠️ POI搜索失败，尝试地理编码...")
                
                if district and district != city:
                    detailed_address = f"{city}{district}{name}"
                else:
                    detailed_address = f"{city}{name}"
                
                coords = await self.geocode(detailed_address, city)
                
                if coords:
                    loc["lat"] = coords["lat"]
                    loc["lng"] = coords["lng"]
                    print(f"   ✅ {name}: ({coords['lat']}, {coords['lng']})")
                else:
                    print(f"   ❌ {name}: 未能获取准确坐标，保留原值")
            
            updated_locations.append(loc)
        
        print(f"✅ 批量地理编码完成\n")
        return updated_locations
    
    def _extract_city(self, name: str, description: str = "") -> str:
        """
        从地点名称或描述中提取城市信息
        
        Args:
            name: 地点名称
            description: 地点描述
            
        Returns:
            城市名称
        """
        # 常见城市列表
        cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", 
                  "重庆", "武汉", "西安", "天津", "苏州", "青岛", "大连",
                  "厦门", "宁波", "烟台", "济南", "郑州", "长沙"]
        
        # 先检查名称中是否包含城市
        text = f"{name} {description}"
        for city in cities:
            if city in text:
                return city
        
        # 默认返回烟台（根据当前项目上下文）
        return "烟台"
    
    def _extract_district(self, name: str, description: str = "", city: str = "") -> str:
        """
        从地点名称或描述中提取区县信息
        
        Args:
            name: 地点名称
            description: 地点描述
            city: 城市名称
            
        Returns:
            区县名称，如果未找到则返回空字符串
        """
        # 烟台市区县列表
        districts = {
            "烟台": ["芝罘区", "莱山区", "福山区", "牟平区", "蓬莱区", 
                    "龙口市", "莱阳市", "莱州市", "招远市", "栖霞市", "海阳市"],
            "北京": ["东城区", "西城区", "朝阳区", "海淀区", "丰台区"],
            "上海": ["黄浦区", "徐汇区", "长宁区", "静安区", "普陀区"],
        }
        
        text = f"{name} {description}"
        
        # 查找匹配的区县
        if city in districts:
            for district in districts[city]:
                if district in text:
                    return district
        
        return ""


# 创建全局地理编码服务实例
geocoding_service = GeocodingService()
