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
    audio_path: str = Field(..., description="音频文件路径")
    extract_text: bool = Field(default=True, description="是否提取文本")

class AudioProcessorTool(BaseTool):
    """音频处理工具 - 使用 qwen-omni 直接分析音频情绪"""
    
    name: str = "音频情绪分析工具"
    description: str = (
        "使用 qwen-omni 模型直接分析音频文件中的情绪和语音特征。"
        "输入参数: audio_path (音频文件路径)"
        "返回: 音频中的情绪特征、语调分析、语速评估等"
    )
    args_schema: Type[BaseModel] = AudioProcessorInput
    
    def _run(self, audio_path: str, extract_text: bool = True) -> str:
        """
        执行音频情绪分析
        
        Args:
            audio_path: 音频文件路径
            extract_text: 是否提取文本（保留参数兼容性）
            
        Returns:
            音频情绪分析结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                return f"错误: 音频文件不存在: {audio_path}"
            
            # 获取文件信息
            file_size = os.path.getsize(audio_path)
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            # 读取音频文件并转换为base64
            try:
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            except Exception as e:
                return f"错误: 无法读取音频文件: {str(e)}"
            
            # 构建音频 URL（data URI 格式）
            # qwen-omni 支持的格式
            mime_types = {
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.m4a': 'audio/mp4',
                '.ogg': 'audio/ogg',
                '.flac': 'audio/flac'
            }
            mime_type = mime_types.get(file_ext, 'audio/wav')
            audio_url = f"data:{mime_type};base64,{audio_base64}"
            
            # 使用 OpenAI SDK 调用 qwen-omni 分析音频
            try:
                client = OpenAI(
                    api_key=config.DASHSCOPE_API_KEY,
                    base_url=config.DASHSCOPE_API_BASE,
                )
                
                # 构建消息，包含音频输入
                messages = [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """请分析这段音频中说话者的情绪状态。请从以下维度进行分析：

1. 语调特征（高昂/低沉/平稳）
2. 语速（快速/正常/缓慢）
3. 音量和能量（高/中/低）
4. 情绪色彩（积极/消极/中性）
5. 可能的情绪类型

请提供详细的分析结果。"""
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_base64,
                                "format": file_ext.lstrip('.')
                            }
                        }
                    ]
                }]
                
                # 调用 API
                response = client.chat.completions.create(
                    model="qwen-audio-turbo",  # 使用 qwen-audio-turbo 模型
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # 提取分析结果
                analysis = response.choices[0].message.content
                
                result = f"""音频情绪分析结果:
文件信息:
- 路径: {audio_path}
- 大小: {file_size} 字节
- 格式: {file_ext}

AI 分析结果:
{analysis}
"""
                return result
                
            except Exception as e:
                # 如果 API 调用失败，返回基础文件信息
                return f"""音频文件信息:
- 文件路径: {audio_path}
- 文件大小: {file_size} 字节
- 文件格式: {file_ext}

注意: 直接音频分析失败 ({str(e)})，建议使用音频文本转写后进行分析。
音频文件已准备好，可以通过其他方式处理。"""
            
        except Exception as e:
            return f"音频处理出错: {str(e)}"
    
    async def _arun(self, audio_path: str, extract_text: bool = True) -> str:
        """异步执行"""
        return self._run(audio_path, extract_text)

