"""
音频处理工具 - 使用 qwen-omni 直接处理音频
"""
from crewai.tools import BaseTool
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
import os
import base64
from openai import OpenAI
from config import config

class AudioProcessorInput(BaseModel):
    """音频处理工具输入模型"""
    audio_path: str = Field(default="", description="音频文件路径（可选）")
    text: str = Field(default="", description="当前文本内容（可选）")
    conversation_history: str = Field(default="", description="对话历史（可选）")

class AudioProcessorTool(BaseTool):
    """音频处理工具 - 使用 qwen-omni 综合分析音频、文本和对话历史"""
    
    name: str = "多模态情绪分析工具"
    description: str = (
        "使用 qwen-omni 模型综合分析音频、文本和对话历史，识别用户的情绪状态。"
        "输入参数: audio_path (音频文件路径), text (当前文本), conversation_history (对话历史)"
        "返回: 完整的情绪分析结果"
    )
    args_schema: Type[BaseModel] = AudioProcessorInput
    
    def _run(self, audio_path: str = "", text: str = "", conversation_history: str = "") -> str:
        """
        执行多模态情绪分析
        
        Args:
            audio_path: 音频文件路径（可选）
            text: 当前文本内容（可选）
            conversation_history: 对话历史（可选）
            
        Returns:
            综合情绪分析结果
        """
        try:
            # 使用 OpenAI SDK 调用 qwen-omni
            client = OpenAI(
                api_key=config.DASHSCOPE_API_KEY,
                base_url=config.DASHSCOPE_API_BASE,
            )
            
            # 构建分析提示词
            analysis_prompt = """请综合分析用户的情绪状态，识别出所有可能的情绪类型。

可选的情绪类型包括但不限于：
开心、快乐、兴奋、满足、悲伤、难过、失落、沮丧、愤怒、生气、烦躁、不满、
焦虑、担心、紧张、恐惧、惊讶、震惊、困惑、平静、放松、淡定、厌恶、反感、
无聊、期待、希望、好奇、感激、感动、温暖、孤独、寂寞、无助、自信、自豪、
骄傲、羞愧、内疚、尴尬、疲惫、困倦、无力

请以 JSON 格式返回分析结果，格式如下：
{
    "emotions": [
        {
            "emotion": "情绪类型",
            "confidence": 0.85,
            "reason": "识别理由"
        }
    ],
    "primary_emotion": "主要情绪",
    "analysis": "综合分析（200字以内）"
}

"""
            
            # 添加对话历史上下文
            if conversation_history:
                analysis_prompt += f"\n对话历史:\n{conversation_history}\n"
            
            # 添加当前文本
            if text:
                analysis_prompt += f"\n当前文本: {text}\n"
            
            # 构建消息内容
            message_content = [
                {
                    "type": "text",
                    "text": analysis_prompt
                }
            ]
            
            # 如果有音频，添加音频输入
            if audio_path and os.path.exists(audio_path):
                # 读取音频文件
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                file_ext = os.path.splitext(audio_path)[1].lstrip('.')
                
                # 处理格式映射（某些格式需要转换）
                format_mapping = {
                    'webm': 'webm',
                    'wav': 'wav',
                    'mp3': 'mp3',
                    'm4a': 'm4a',
                    'ogg': 'ogg',
                    'flac': 'flac'
                }
                audio_format = format_mapping.get(file_ext, 'wav')
                
                message_content.append({
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_base64,
                        "format": audio_format
                    }
                })
            
            # 调用 API
            response = client.chat.completions.create(
                model="qwen-audio-turbo" if audio_path else config.QWEN_LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                extra_body={'enable_thinking': config.ENABLE_THINKING},
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS
            )
            
            # 提取分析结果
            analysis = response.choices[0].message.content
            
            return analysis
            
        except Exception as e:
            return f"情绪分析失败: {str(e)}"
    
    async def _arun(self, audio_path: str = "", text: str = "", conversation_history: str = "") -> str:
        """异步执行"""
        return self._run(audio_path, text, conversation_history)

