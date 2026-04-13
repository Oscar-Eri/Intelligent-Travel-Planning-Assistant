import asyncio
import httpx

async def test_xingfu_street():
    """测试幸福街道聊天API"""
    
    print("="*60)
    print("测试: 我想去烟台市芝罘区幸福街道逛两天")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            'http://localhost:8000/api/chat',
            json={
                'messages': [
                    {'role': 'user', 'content': '我想去烟台市芝罘区幸福街道逛两天'}
                ]
            }
        )
        
        print(f'\n状态码: {response.status_code}')
        data = response.json()
        
        print(f'\n标题: {data.get("itinerary_title")}')
        print(f'地点数量: {len(data.get("locations") or [])}')
        print(f'\n完整响应数据:')
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('locations'):
            print(f'\n✅ 地点列表:')
            for i, loc in enumerate(data['locations'], 1):
                print(f'{i}. {loc["name"]} ({loc["lat"]}, {loc["lng"]}) - {loc.get("time", "")}')
                print(f'   {loc.get("description", "")}')
        else:
            print(f'\n❌ 没有返回地点信息')
            print('\n这说明问题可能是：')
            print('1. LLM没有返回JSON格式')
            print('2. JSON解析失败')
            print('3. locations字段为空或None')
        
        print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_xingfu_street())
