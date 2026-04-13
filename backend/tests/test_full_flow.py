import asyncio
import httpx
import json

async def test_full_flow():
    """测试完整流程：从用户输入到地理编码"""
    
    print("="*80)
    print("测试完整流程：用户输入 -> LLM生成 -> 地理编码 -> 返回结果")
    print("="*80)
    
    async with httpx.AsyncClient(timeout=60) as client:
        # 发送请求
        print("\n📤 发送请求...")
        response = await client.post(
            'http://localhost:8000/api/chat',
            json={
                'messages': [
                    {'role': 'user', 'content': '我想去烟台市芝罘区幸福街道逛两天'}
                ]
            }
        )
        
        print(f"✅ 响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.text}")
            return
        
        data = response.json()
        
        print(f"\n📊 响应数据分析:")
        print(f"   itinerary_title: {data.get('itinerary_title')}")
        print(f"   response 长度: {len(data.get('response', ''))}")
        print(f"   locations 类型: {type(data.get('locations'))}")
        
        locations = data.get('locations')
        
        if locations is None:
            print(f"\n❌ 错误: locations 为 None!")
            print(f"   这说明LLM没有正确返回地点数据")
            return
        
        if not isinstance(locations, list):
            print(f"\n❌ 错误: locations 不是列表类型!")
            print(f"   实际类型: {type(locations)}")
            return
        
        if len(locations) == 0:
            print(f"\n⚠️ 警告: locations 是空列表")
            return
        
        print(f"   locations 数量: {len(locations)}")
        
        print(f"\n📍 地点详细信息:")
        for i, loc in enumerate(locations, 1):
            print(f"\n   [{i}] {loc.get('name')}")
            print(f"       纬度 (lat): {loc.get('lat')}")
            print(f"       经度 (lng): {loc.get('lng')}")
            print(f"       时间: {loc.get('time')}")
            print(f"       描述: {loc.get('description')[:50]}...")
            
            # 验证坐标是否合理（烟台范围）
            lat = loc.get('lat', 0)
            lng = loc.get('lng', 0)
            
            # 烟台市大致范围: lat 37.0-38.0, lng 120.5-122.0
            if 37.0 <= lat <= 38.0 and 120.5 <= lng <= 122.0:
                print(f"       ✅ 坐标在烟台范围内")
            else:
                print(f"       ⚠️ 坐标可能不在烟台范围内!")
        
        print(f"\n{'='*80}")
        print("✅ 测试完成!")
        print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
