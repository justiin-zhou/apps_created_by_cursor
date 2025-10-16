"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional


class TranscriptionRequest(BaseModel):
    """转写请求"""
    text_content: Optional[str] = Field(None, description="会议文本内容（如果不上传音频文件）")
    language: str = Field("zh", description="语言代码")


class SummaryRequest(BaseModel):
    """纪要生成请求"""
    transcription: str = Field(..., description="会议转写文本")


class QuestionRequest(BaseModel):
    """问答请求"""
    meeting_content: str = Field(..., description="会议内容")
    question: str = Field(..., description="问题")


class TranscriptionResponse(BaseModel):
    """转写响应"""
    raw_transcription: str
    formatted_transcription: str
    status: str


class SummaryResponse(BaseModel):
    """纪要响应"""
    summary: str
    status: str


class QuestionResponse(BaseModel):
    """问答响应"""
    question: str
    answer: str
    status: str


class FullMeetingResponse(BaseModel):
    """完整会议处理响应"""
    transcription: dict
    summary: dict
    status: str


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None

