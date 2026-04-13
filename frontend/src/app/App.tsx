import { useState, useRef, useEffect } from 'react';
import { Send, MapPin, Sparkles } from 'lucide-react';
import { TravelMap, Location } from './components/TravelMap';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  locations?: Location[];
  itineraryTitle?: string;
}

// Mock travel plans database
const mockTravelPlans: Record<string, { locations: Location[]; response: string; title: string }> = {
  北京: {
    title: '北京两日游',
    locations: [
      {
        name: '天安门广场',
        lat: 39.9042,
        lng: 116.3976,
        time: '第1天 08:00-10:00',
        description: '参观天安门广场，观看升旗仪式，感受祖国的庄严与壮丽'
      },
      {
        name: '故宫博物院',
        lat: 39.9163,
        lng: 116.3972,
        time: '第1天 10:00-14:00',
        description: '游览紫禁城，探索明清两代皇家宫殿的辉煌历史'
      },
      {
        name: '景山公园',
        lat: 39.9253,
        lng: 116.3948,
        time: '第1天 14:30-16:00',
        description: '登顶景山，俯瞰故宫全景，欣赏北京城市风光'
      },
      {
        name: '南锣鼓巷',
        lat: 39.9371,
        lng: 116.4037,
        time: '第1天 17:00-19:00',
        description: '漫步古老胡同，品尝北京小吃，体验老北京文化'
      },
      {
        name: '八达岭长城',
        lat: 40.3594,
        lng: 116.0144,
        time: '第2天 08:00-14:00',
        description: '攀登万里长城，感受中华民族的智慧与力量'
      },
      {
        name: '颐和园',
        lat: 39.9998,
        lng: 116.2754,
        time: '第2天 15:00-18:00',
        description: '游览皇家园林，欣赏昆明湖美景，体验园林艺术'
      },
      {
        name: '王府井大街',
        lat: 39.9141,
        lng: 116.4167,
        time: '第2天 19:00-21:00',
        description: '品尝王府井小吃街美食，购物休闲，结束愉快的旅程'
      }
    ],
    response: '**第一天：文化古迹之旅**\n• 早上观看天安门升旗仪式\n• 参观故宫博物院（建议提前预约门票）\n• 登景山公园俯瞰故宫全景\n• 傍晚逛南锣鼓巷，品尝老北京美食\n\n**第二天：自然与园林**\n• 早起前往八达岭长城（约2小时车程）\n• 下午游览颐和园皇家园林\n• 晚上在王府井大街购物和品尝美食\n\n**交通建议：**\n使用地铁和公交出行方便快捷。长城需要提前预约专线巴士或跟团。'
  }
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: '你好!我是你的旅游规划AI助手。😊\n\n我可以帮你规划旅行行程,包括景点推荐、路线安排等。请告诉我:\n\n1️⃣ 你想去哪个城市?\n2️⃣ 你有多少天时间?\n3️⃣ 有什么特别想去的景点吗?\n\n例如:"我有两天时间逛南京,该怎么安排?"',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentItinerary, setCurrentItinerary] = useState<{
    locations: Location[];
    title: string;
  } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleModification = (userInput: string, currentLocations: Location[]) => {
    const input = userInput.toLowerCase();
    let newLocations = [...currentLocations];
    let responseText = '';

    // 删除景点
    if (input.includes('删除') || input.includes('去掉') || input.includes('不去')) {
      const locationToRemove = currentLocations.find(loc =>
        input.includes(loc.name.toLowerCase()) || input.includes(loc.name)
      );

      if (locationToRemove) {
        newLocations = currentLocations.filter(loc => loc.name !== locationToRemove.name);
        responseText = `好的，我已经将「${locationToRemove.name}」从行程中删除了。下面是更新后的行程：`;
        return { locations: newLocations, response: responseText };
      }
    }

    // 添加景点
    if (input.includes('添加') || input.includes('加上') || input.includes('增加')) {
      if (input.includes('鸟巢') || input.includes('水立方')) {
        const newLocation: Location = {
          name: '鸟巢/水立方',
          lat: 39.9928,
          lng: 116.3903,
          time: '第2天 09:00-12:00',
          description: '参观2008年奥运会主场馆，感受现代建筑的魅力'
        };
        newLocations.splice(4, 0, newLocation);
        responseText = '好的，我已经将「鸟巢/水立方」添加到第2天的行程中。下面是更新后的行程：';
        return { locations: newLocations, response: responseText };
      }

      if (input.includes('天坛')) {
        const newLocation: Location = {
          name: '天坛公园',
          lat: 39.8828,
          lng: 116.4068,
          time: '第1天 16:00-17:30',
          description: '游览明清两代皇帝祭天的场所，欣赏古代建筑艺术'
        };
        newLocations.splice(3, 0, newLocation);
        responseText = '好的，我已经将「天坛公园」添加到第1天的行程中。下面是更新后的行程：';
        return { locations: newLocations, response: responseText };
      }
    }

    // 调整时间
    if (input.includes('提前') || input.includes('推迟') || input.includes('改到')) {
      responseText = '好的，我已经调整了时间安排。下面是更新后的行程：';
      return { locations: newLocations, response: responseText };
    }

    // 交换顺序
    if (input.includes('先去') || input.includes('调换') || input.includes('换一下')) {
      responseText = '好的，我已经调整了景点顺序。下面是更新后的行程：';
      return { locations: newLocations, response: responseText };
    }

    return null;
  };

  const handleSend = async () => {
    if (!input.trim()) return;
  
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };
  
    setMessages((prev) => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setIsLoading(true);
  
    try {
      // 构建消息历史（排除系统消息）
      const messageHistory = messages
        .filter(msg => msg.id !== '0') // 排除欢迎消息
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }));
  
      // 调用后端API
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          messages: [
            ...messageHistory,
            { role: 'user', content: userInput }
          ]
        })
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      const data = await response.json();
  
      // 调试日志：打印后端返回的数据
      console.log('=== 后端响应数据 ===');
      console.log('完整数据:', data);
      console.log('locations:', data.locations);
      console.log('locations类型:', typeof data.locations);
      console.log('locations是否为数组:', Array.isArray(data.locations));
      console.log('locations长度:', data.locations?.length);
      console.log('itinerary_title:', data.itinerary_title);
      console.log('==================');
  
      // 更新当前行程状态
      if (data.locations && data.locations.length > 0) {
        setCurrentItinerary({
          locations: data.locations,
          title: data.itinerary_title || '旅游行程'
        });
      }
  
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        locations: data.locations,
        itineraryTitle: data.itinerary_title
      };
  
      console.log('📤 即将添加的AI消息:', aiMessage);
      console.log('aiMessage.locations:', aiMessage.locations);
  
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('请求失败:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉,服务器连接失败。请确保后端服务正在运行。',
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-green-600 rounded-full flex items-center justify-center">
              <MapPin className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">旅游规划AI助手</h1>
              <p className="text-sm text-gray-500">智能规划你的完美旅程</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message) => {
            // 调试日志
            if (message.role === 'assistant' && message.locations) {
              console.log('🗺️ 渲染消息 - ID:', message.id);
              console.log('   locations数量:', message.locations.length);
              console.log('   itineraryTitle:', message.itineraryTitle);
            }
            
            return (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex gap-3 max-w-3xl ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${
                  message.role === 'user' ? 'bg-blue-600' : 'bg-gradient-to-br from-green-500 to-blue-500'
                }`}>
                  {message.role === 'user' ? (
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  ) : (
                    <Sparkles className="w-5 h-5 text-white" />
                  )}
                </div>

                {/* Message content */}
                <div className="flex-1">
                  {message.role === 'user' ? (
                    <div
                      className="rounded-2xl px-5 py-3 bg-blue-600 text-white"
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    </div>
                  ) : (
                    <>
                      {/* Map first if exists */}
                      {message.locations && message.locations.length > 0 && (
                        <div className="mb-4">
                          <TravelMap locations={message.locations} />
                        </div>
                      )}

                      {/* Then text content */}
                      <div className="rounded-2xl px-5 py-3 bg-white border border-gray-200 text-gray-900 shadow-sm">
                        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                      </div>
                    </>
                  )}

                  <p className="text-xs text-gray-400 mt-2 px-2">
                    {message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="bg-white border-t border-gray-200 shadow-lg">
        <div className="max-w-4xl mx-auto px-6 py-4">
          {currentItinerary && (
            <div className="mb-3 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
              <span className="font-semibold">当前行程：</span>{currentItinerary.title}
              <span className="ml-2 text-blue-600">（可以说"删除某景点"、"添加天坛"等来修改行程）</span>
            </div>
          )}
          <div className="flex gap-3 items-end">
            <div className="flex-1 bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-200 transition-all">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入你的旅行需求，比如：我有两天时间逛北京，该怎么安排？"
                className="w-full px-5 py-3 bg-transparent resize-none focus:outline-none text-gray-900 placeholder-gray-400"
                rows={1}
                style={{
                  minHeight: '48px',
                  maxHeight: '120px'
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = target.scrollHeight + 'px';
                }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
