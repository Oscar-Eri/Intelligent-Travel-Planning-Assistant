"""
LLM 服务层 - 负责与通义千问 API 交互
"""
import httpx
from typing import List, Dict, AsyncGenerator
from config import settings


class LLMService:
    """LLM 服务类 - 封装所有 LLM 相关操作"""
    
    def __init__(self):
        self.base_url = settings.QWEN_BASE_URL
        self.api_key = settings.QWEN_API_KEY
        self.model = settings.QWEN_MODEL
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        调用 LLM 完成对话
        
        Args:
            messages: 消息列表，格式为 [{"role": "user/assistant", "content": "..."}]
            stream: 是否使用流式响应
            
        Yields:
            生成的文本片段
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        url = f"{self.base_url}/chat/completions"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                if stream:
                    # 流式响应
                    async with client.stream("POST", url, json=payload, headers=headers) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]  # 去掉 "data: " 前缀
                                if data == "[DONE]":
                                    break
                                yield data
                else:
                    # 非流式响应
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    yield content
                    
        except httpx.HTTPError as e:
            raise Exception(f"LLM API 请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"LLM 调用出错: {str(e)}")
    
    async def generate_travel_plan(
        self, 
        user_input: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict:
        """
        生成旅行计划
        
        Args:
            user_input: 用户输入
            conversation_history: 对话历史（可选）
            
        Returns:
            包含 response、locations、itinerary_title 的字典
        """
        system_prompt = """You are a professional travel planning AI assistant. Your task is:

1. Recommend suitable tourist attractions based on user needs
2. Arrange a logical and efficient itinerary (time and route)
3. Provide detailed descriptions and practical travel advice
4. Return structured itinerary data in JSON format

Important Principles:
- Even if the user provides incomplete information, generate a reasonable default itinerary
- For popular destinations, directly generate a classic 1–3 day itinerary
- If more information would help, mention it in "response", but still provide a complete example
- Only omit "locations" if the destination cannot be determined

When the user mentions a city or region:
- Provide a detailed itinerary with time, locations, and descriptions
- Location names MUST be accurate official names
- Description MUST include full address: "Located in {City}{District}{Street}, ..."
- Set lat and lng to 0 (system will auto-geocode via AMap API)
- Provide useful transportation and travel tips
- Default to 2-day itinerary unless specified otherwise

CRITICAL JSON FORMAT REQUIREMENTS:
- Return ONLY valid JSON, no extra text before or after
- Keep location names concise (max 20 characters)
- Keep descriptions concise (max 50 characters)
- Ensure all brackets and quotes are properly closed
- Test your JSON output for validity before returning

Return in this EXACT JSON format:
{
  "title": "Trip Title",
  "response": "Detailed itinerary explanation (Markdown supported)",
  "locations": [
    {
      "name": "Official location name",
      "lat": 0,
      "lng": 0,
      "time": "Day 1 09:00-11:00",
      "description": "Located in City District Street..."
    }
  ]
}

Notes:
- lat/lng must be 0 (system uses AMap POI search for accuracy)
- description MUST include full address (City + District + Street)
- Keep content concise to avoid JSON truncation
- If just greeting, respond normally without JSON
- If city/region mentioned, JSON with locations is mandatory"""

        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            response_text = ""
            async for chunk in self.chat_completion(messages, stream=False):
                response_text += chunk
            
            # 调试日志：打印LLM原始响应
            print(f"\n{'='*60}")
            print(f"用户输入: {user_input}")
            print(f"LLM原始响应:\n{response_text}")
            print(f"{'='*60}\n")
            
            # 尝试解析JSON
            import json
            try:
                # 查找JSON部分
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end]
                    plan_data = json.loads(json_str)
                    
                    print(f"✅ 成功解析JSON")
                    print(f"   plan_data keys: {list(plan_data.keys())}")
                    print(f"   locations 类型: {type(plan_data.get('locations'))}")
                    print(f"   locations 值: {plan_data.get('locations')}")
                    
                    # 检查 locations 是否为 None 或空
                    locations = plan_data.get("locations")
                    if locations is None:
                        print(f"⚠️ locations 为 None，尝试从 response 中提取")
                        # 可能 LLM 把 JSON 放在了 response 字段中
                        response_content = plan_data.get("response", "")
                        if isinstance(response_content, str):
                            # 尝试从 response 字符串中提取 JSON
                            nested_json_start = response_content.find('{')
                            nested_json_end = response_content.rfind('}') + 1
                            if nested_json_start != -1 and nested_json_end != -1:
                                try:
                                    nested_json_str = response_content[nested_json_start:nested_json_end]
                                    nested_data = json.loads(nested_json_str)
                                    print(f"✅ 成功从 response 中提取嵌套 JSON")
                                    locations = nested_data.get("locations", [])
                                    plan_data["response"] = nested_data.get("response", plan_data.get("response", ""))
                                    plan_data["title"] = nested_data.get("title", plan_data.get("title", "旅游行程"))
                                except json.JSONDecodeError:
                                    print(f"❌ 嵌套 JSON 解析失败")
                                    locations = []
                            else:
                                locations = []
                        else:
                            locations = []
                    
                    print(f"✅ 最终 locations 数量: {len(locations) if locations else 0}")
                    
                    return {
                        "response": plan_data.get("response", response_text[:json_start].strip()),
                        "locations": locations if locations else [],
                        "itinerary_title": plan_data.get("title", "旅游行程")
                    }
                else:
                    # 没有JSON，直接返回文本
                    print(f"⚠️ 未找到JSON格式，返回纯文本")
                    return {
                        "response": response_text,
                        "locations": [],
                        "itinerary_title": None
                    }
            except json.JSONDecodeError as e:
                # JSON解析失败，返回纯文本
                print(f"❌ JSON解析失败: {e}")
                return {
                    "response": response_text,
                    "locations": [],
                    "itinerary_title": None
                }
                
        except Exception as e:
            raise Exception(f"生成旅行计划失败: {str(e)}")


# 创建全局LLM服务实例
llm_service = LLMService()
