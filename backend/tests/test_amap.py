import asyncio
import httpx

async def test_amap_api():
    """测试高德地图API"""
    
    api_key = "242ea7c83bf702a32046bc75c83dbb0d"
    address = "烟台市芝罘区幸福码头"
    
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "key": api_key,
        "address": address,
        "output": "json"
    }
    
    print("="*60)
    print(f"测试高德地图地理编码API")
    print(f"地址: {address}")
    print("="*60)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            print(f"\n响应状态: {data.get('status')}")
            print(f"返回数量: {data.get('count')}")
            
            if data.get("status") == "1" and data.get("count") != "0":
                geocode = data["geocodes"][0]
                location_str = geocode["location"]
                lng, lat = location_str.split(",")
                
                print(f"\n✅ 地理编码成功!")
                print(f"   格式化地址: {geocode.get('formatted_address')}")
                print(f"   纬度 (lat): {lat}")
                print(f"   经度 (lng): {lng}")
                print(f"   置信度: {geocode.get('level')}")
            else:
                print(f"\n❌ 地理编码失败")
                print(f"   信息: {data.get('info')}")
                
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_amap_api())
