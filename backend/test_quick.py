"""
多智能体系统快速测试 - 仅测试架构核心功能
不调用LLM API，速度快
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from agents.mcp_protocol import MCPMessage, MessageType, MessagePriority
from agents.message_bus import message_bus
from agents.coordinator_agent import coordinator_agent
from agents.travel_planner_agent import travel_planner_agent
from agents.geo_coder_agent import geo_coder_agent
from agents.memory_manager_agent import memory_manager_agent


async def test_1_agent_registration():
    """测试1：智能体注册"""
    print("\n" + "="*60)
    print("测试1：智能体注册")
    print("="*60)
    
    registered = message_bus.get_registered_agents()
    print(f"✅ 已注册 {len(registered)} 个智能体:")
    for agent in registered:
        print(f"   - {agent}")
    
    expected_agents = ["coordinator", "travel_planner", "geo_coder", "memory_manager"]
    for agent in expected_agents:
        assert agent in registered, f"❌ 智能体 {agent} 未注册"
    
    print("✅ 所有智能体已成功注册")
    return True


async def test_2_mcp_message():
    """测试2：MCP消息格式"""
    print("\n" + "="*60)
    print("测试2：MCP消息格式")
    print("="*60)
    
    import uuid
    msg = MCPMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.REQUEST,
        sender="test",
        receiver="coordinator",
        action="test_action",
        payload={"key": "value"},
        priority=MessagePriority.NORMAL
    )
    
    print(f"✅ 消息创建成功:")
    print(f"   ID: {msg.message_id[:8]}...")
    print(f"   类型: {msg.message_type}")
    print(f"   发送者: {msg.sender}")
    print(f"   接收者: {msg.receiver}")
    print(f"   动作: {msg.action}")
    
    assert msg.message_type == MessageType.REQUEST
    assert msg.priority == MessagePriority.NORMAL
    
    print("✅ MCP消息格式验证通过")
    return True


async def test_3_intent_recognition():
    """测试3：协调者能力查询"""
    print("\n" + "="*60)
    print("测试3：协调者智能体能力")
    print("="*60)
    
    import uuid
    
    # 获取协调者能力
    response = await message_bus.send_message(MCPMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.REQUEST,
        sender="test",
        receiver="coordinator",
        action="get_capabilities",
        payload={}
    ))
    
    if response.success:
        caps = response.data
        print(f"✅ 协调者智能体能力:")
        print(f"   智能体: {caps.get('agent_name')}")
        print(f"   能力: {', '.join(caps.get('capabilities', []))}")
        print(f"   动作: {', '.join(caps.get('actions', []))}")
    else:
        print(f"❌ 获取能力失败: {response.error}")
        return False
    
    print("✅ 协调者智能体测试通过")
    return True


async def test_4_memory_operations():
    """测试4：记忆管理操作"""
    print("\n" + "="*60)
    print("测试4：记忆管理操作")
    print("="*60)
    
    import uuid
    
    # 保存行程
    save_response = await message_bus.send_message(MCPMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.REQUEST,
        sender="test",
        receiver="memory_manager",
        action="save_itinerary",
        payload={
            "title": "测试行程",
            "locations": [
                {"name": "地点1", "lat": 37.0, "lng": 121.0, "time": "上午", "description": "测试"}
            ]
        }
    ))
    
    if not save_response.success:
        print(f"❌ 行程保存失败: {save_response.error}")
        return False
    
    print("✅ 行程保存成功")
    
    # 获取行程
    get_response = await message_bus.send_message(MCPMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.REQUEST,
        sender="test",
        receiver="memory_manager",
        action="get_itinerary",
        payload={}
    ))
    
    if get_response.success and get_response.data:
        print(f"✅ 行程获取成功:")
        print(f"   标题: {get_response.data.get('title')}")
        print(f"   地点数: {len(get_response.data.get('locations', []))}")
    else:
        print(f"❌ 行程获取失败")
        return False
    
    # 清除行程
    clear_response = await message_bus.send_message(MCPMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.REQUEST,
        sender="test",
        receiver="memory_manager",
        action="clear_itinerary",
        payload={}
    ))
    
    if clear_response.success:
        print("✅ 行程清除成功")
    else:
        print(f"❌ 行程清除失败: {clear_response.error}")
        return False
    
    print("✅ 记忆管理智能体测试通过")
    return True


async def test_5_message_routing():
    """测试5：消息路由机制"""
    print("\n" + "="*60)
    print("测试5：消息路由机制")
    print("="*60)
    
    import uuid
    
    # 测试发送到不存在的智能体
    error_response = await message_bus.send_message(MCPMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.REQUEST,
        sender="test",
        receiver="non_existent_agent",
        action="test",
        payload={}
    ))
    
    if not error_response.success:
        print(f"✅ 错误处理正确: {error_response.error}")
    else:
        print(f"❌ 应该返回错误但未返回")
        return False
    
    # 测试获取智能体能力
    capability_response = await message_bus.send_message(MCPMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.REQUEST,
        sender="test",
        receiver="coordinator",
        action="get_capabilities",
        payload={}
    ))
    
    if capability_response.success:
        caps = capability_response.data
        print(f"✅ 获取能力成功:")
        print(f"   智能体: {caps.get('agent_name')}")
        print(f"   能力数: {len(caps.get('capabilities', []))}")
        print(f"   动作数: {len(caps.get('actions', []))}")
    else:
        print(f"❌ 获取能力失败: {capability_response.error}")
        return False
    
    print("✅ 消息路由机制测试通过")
    return True


async def test_6_geo_coder_capability():
    """测试6：地理编码智能体能力"""
    print("\n" + "="*60)
    print("测试6：地理编码智能体能力查询")
    print("="*60)
    
    import uuid
    
    response = await message_bus.send_message(MCPMessage(
        message_id=str(uuid.uuid4()),
        message_type=MessageType.REQUEST,
        sender="test",
        receiver="geo_coder",
        action="get_capabilities",
        payload={}
    ))
    
    if response.success:
        caps = response.data
        print(f"✅ 地理编码智能体能力:")
        print(f"   智能体: {caps.get('agent_name')}")
        print(f"   能力: {', '.join(caps.get('capabilities', []))}")
        print(f"   动作: {', '.join(caps.get('actions', []))}")
    else:
        print(f"❌ 获取能力失败: {response.error}")
        return False
    
    print("✅ 地理编码智能体测试通过")
    return True


async def main():
    """运行所有快速测试"""
    print("\n" + "🧪 " * 30)
    print("多智能体系统快速测试（不调用LLM）")
    print("🧪 " * 30)
    
    tests = [
        ("智能体注册", test_1_agent_registration),
        ("MCP消息格式", test_2_mcp_message),
        ("协调者意图识别", test_3_intent_recognition),
        ("记忆管理操作", test_4_memory_operations),
        ("消息路由机制", test_5_message_routing),
        ("地理编码能力", test_6_geo_coder_capability),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("="*60)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有架构测试通过！")
        print("\n💡 提示：")
        print("   - 以上测试验证了多智能体架构的核心功能")
        print("   - 未调用LLM API，因此速度很快")
        print("   - 如需测试完整LLM流程，请运行: python test_multi_agent.py")
    else:
        print(f"⚠️  {total - passed} 个测试失败")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
