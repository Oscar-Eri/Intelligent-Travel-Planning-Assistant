"""
MCP协议定义 - 智能体间通信标准
实现高内聚低耦合的核心机制
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime


class MessageType(str, Enum):
    """消息类型枚举"""
    REQUEST = "request"           # 请求
    RESPONSE = "response"         # 响应
    NOTIFICATION = "notification" # 通知
    ERROR = "error"              # 错误


class MessagePriority(str, Enum):
    """消息优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MCPMessage(BaseModel):
    """
    MCP标准消息格式
    
    所有智能体之间的通信都通过此消息格式进行
    实现解耦和标准化
    """
    message_id: str = Field(..., description="消息唯一ID")
    message_type: MessageType = Field(..., description="消息类型")
    sender: str = Field(..., description="发送者智能体名称")
    receiver: str = Field(..., description="接收者智能体名称")
    action: str = Field(..., description="动作/命令")
    payload: Dict[str, Any] = Field(default_factory=dict, description="消息负载数据")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="优先级")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MCPResponse(BaseModel):
    """MCP标准响应格式"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    message_id: Optional[str] = Field(None, description="关联的请求消息ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class AgentCapability(BaseModel):
    """智能体能力描述"""
    agent_name: str = Field(..., description="智能体名称")
    capabilities: List[str] = Field(..., description="支持的能力列表")
    actions: List[str] = Field(..., description="支持的动作列表")
    version: str = Field(default="1.0.0", description="版本")
    description: str = Field(default="", description="描述")
