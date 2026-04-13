"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Location(BaseModel):
    """地点信息模型"""
    name: str = Field(..., description="地点名称")
    lat: float = Field(..., description="纬度")
    lng: float = Field(..., description="经度")
    time: str = Field(..., description="时间安排")
    description: str = Field(..., description="地点描述")


class Message(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="角色：user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[Message] = Field(..., description="对话历史")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI回复内容")
    locations: Optional[List[Location]] = Field(default_factory=list, description="行程地点列表")
    itinerary_title: Optional[str] = Field(None, description="行程标题")


class TravelPlan(BaseModel):
    """旅行计划模型"""
    title: str = Field(..., description="行程标题")
    locations: List[Location] = Field(..., description="地点列表")
    response: str = Field(..., description="行程说明文本")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
