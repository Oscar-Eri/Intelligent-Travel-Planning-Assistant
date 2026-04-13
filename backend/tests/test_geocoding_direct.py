import asyncio
from services.geocoding_service import geocoding_service

async def test_geocoding_directly():
    """直接测试地理编码服务"""
    
    print("="*80)
    print("直接测试地理编码服务")
    print("="*80)
    
    # 测试几个地点
    test_locations = [
        {"name": "烟台山历史文化街区", "description": "烟台发祥地"},
        {"name": "幸福码头", "description": "芝罘区幸福街道"},
        {"name": "所城里历史文化街区", "description": "烟台建城之始"},
    ]
    
    print(f"\n📍 测试 {len(test_locations)} 个地点的地理编码:\n")
    
    for loc in test_locations:
        print(f"地点: {loc['name']}")
        print(f"描述: {loc['description']}")
        
        # 调用地理编码
        coords = await geocoding_service.geocode(loc['name'], "烟台")
        
        if coords:
            print(f"✅ 地理编码成功:")
            print(f"   纬度: {coords['lat']}")
            print(f"   经度: {coords['lng']}")
            
            # 验证是否在烟台范围内
            if 37.0 <= coords['lat'] <= 38.0 and 120.5 <= coords['lng'] <= 122.0:
                print(f"   ✅ 坐标在烟台合理范围内")
            else:
                print(f"   ⚠️ 坐标可能不在烟台范围内!")
        else:
            print(f"❌ 地理编码失败")
        
        print()
    
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_geocoding_directly())
