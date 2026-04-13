"""
后端 API 测试脚本
"""
import requests
import json


# API 基础地址
BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查接口"""
    print("=" * 60)
    print("测试 1: 健康检查")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_chat_basic():
    """测试基本聊天功能"""
    print("=" * 60)
    print("测试 2: 基本聊天（打招呼）")
    print("=" * 60)
    
    payload = {
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"回复: {result['response']}")
    locations = result.get('locations') or []
    print(f"地点数量: {len(locations)}")
    print()


def test_chat_beijing():
    """测试北京旅行规划"""
    print("=" * 60)
    print("测试 3: 北京旅行规划")
    print("=" * 60)
    
    payload = {
        "messages": [
            {"role": "user", "content": "我有两天时间逛北京，该怎么安排？"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"行程标题: {result.get('itinerary_title')}")
    print(f"回复长度: {len(result['response'])} 字符")
    locations = result.get('locations') or []
    print(f"地点数量: {len(locations)}")
    
    if locations:
        print("\n景点列表:")
        for i, loc in enumerate(result['locations'], 1):
            print(f"  {i}. {loc['name']} - {loc['time']}")
    print()


def test_get_itinerary():
    """测试获取当前行程"""
    print("=" * 60)
    print("测试 4: 获取当前行程")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/itinerary")
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"行程标题: {result.get('title')}")
    locations = result.get('locations') or []
    print(f"地点数量: {len(locations)}")
    print()


def test_delete_itinerary():
    """测试清除行程"""
    print("=" * 60)
    print("测试 5: 清除当前行程")
    print("=" * 60)
    
    response = requests.delete(f"{BASE_URL}/api/itinerary")
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {result['message']}")
    print()


def main():
    """运行所有测试"""
    print("\n")
    print("🚀 开始测试旅行地图后端 API")
    print("=" * 60)
    print()
    
    try:
        # 检查服务是否运行
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
        except requests.exceptions.ConnectionError:
            print("❌ 错误: 无法连接到后端服务")
            print("   请确保后端服务已启动: python main.py")
            return
        
        # 运行测试
        test_health()
        test_chat_basic()
        test_chat_beijing()
        test_get_itinerary()
        test_delete_itinerary()
        
        print("=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")


if __name__ == "__main__":
    main()
