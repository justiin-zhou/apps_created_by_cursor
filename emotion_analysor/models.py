"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EmotionDetectRequest(BaseModel):
    """情绪识别请求模型"""
    text: Optional[str] = Field(None, description="文本内容")
    audio_url: Optional[str] = Field(None, description="音频文件URL或路径")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default_factory=list, 
        description="对话历史"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "今天真的太开心了！",
                "audio_url": "/uploads/audio.wav",
                "conversation_history": [
                    {"role": "user", "content": "我今天遇到了一件事"},
                    {"role": "assistant", "content": "什么事情呢？"}
                ]
            }
        }

class EmotionResult(BaseModel):
    """单个情绪结果"""
    emotion: str = Field(..., description="情绪类型")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度 (0-1)")
    reason: str = Field(..., description="识别理由")

class EmotionDetectResponse(BaseModel):
    """情绪识别响应模型"""
    success: bool = Field(..., description="是否成功")
    emotions: List[EmotionResult] = Field(..., description="识别出的情绪列表")
    primary_emotion: str = Field(..., description="主要情绪")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "emotions": [
                    {
                        "emotion": "开心",
                        "confidence": 0.95,
                        "reason": "用户使用了积极的语气词和表情"
                    },
                    {
                        "emotion": "兴奋",
                        "confidence": 0.82,
                        "reason": "语调高亢，语速较快"
                    }
                ],
                "primary_emotion": "开心",
                "timestamp": "2025-10-16T12:00:00"
            }
        }

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = Field(default="1.0.0", description="版本号")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False)
    error: str = Field(..., description="错误信息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

