"""
音频转写工具
"""
import os
import openai
from typing import Optional
from config import WHISPER_API_KEY, WHISPER_API_BASE


class TranscriptionTool:
    """
    音频转写工具类
    使用 Whisper API 进行音频转文本
    注意：DeepSeek 暂不支持语音识别，需要使用 OpenAI Whisper 或其他服务
    """
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=WHISPER_API_KEY,
            base_url=WHISPER_API_BASE
        )
    
    def transcribe_audio(self, audio_file_path: str, language: str = "zh") -> dict:
        """
        转写音频文件
        
        Args:
            audio_file_path: 音频文件路径
            language: 语言代码，默认为中文
            
        Returns:
            包含转写文本和元数据的字典
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                # 使用OpenAI Whisper API进行转写
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            
            # 构建结构化的转写结果
            result = {
                "text": transcript.text,
                "language": transcript.language if hasattr(transcript, 'language') else language,
                "duration": transcript.duration if hasattr(transcript, 'duration') else None,
                "segments": []
            }
            
            # 如果有分段信息，添加到结果中
            if hasattr(transcript, 'segments') and transcript.segments:
                for segment in transcript.segments:
                    result["segments"].append({
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0),
                        "text": segment.get("text", "")
                    })
            
            return result
            
        except Exception as e:
            return {
                "error": f"转写失败: {str(e)}",
                "text": "",
                "segments": []
            }
    
    def transcribe_text(self, text: str) -> dict:
        """
        处理已有的文本内容（用于测试或直接提供文本的场景）
        
        Args:
            text: 会议文本内容
            
        Returns:
            格式化的文本字典
        """
        return {
            "text": text,
            "language": "zh",
            "duration": None,
            "segments": []
        }

