"""
情绪识别服务 - 直接使用 qwen-omni 完成多模态情绪识别
"""
from typing import Dict, List, Optional, Any
import json
import logging
import os
import base64
from openai import OpenAI

from models import EmotionDetectRequest, EmotionDetectResponse, EmotionResult
from config import config

logger = logging.getLogger(__name__)

class EmotionDetectionCrew:
    """情绪识别服务 - 直接使用 qwen-omni 进行多模态分析"""
    
    def __init__(self):
        """初始化服务"""
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=config.DASHSCOPE_API_KEY,
            base_url=config.DASHSCOPE_API_BASE,
        )
        
        logger.info("EmotionDetectionCrew 初始化完成（直接使用 OpenAI SDK）")
    
    def analyze_emotion(
        self,
        request: EmotionDetectRequest
    ) -> EmotionDetectResponse:
        """
        执行情绪识别分析
        
        Args:
            request: 情绪识别请求
            
        Returns:
            情绪识别结果
        """
        try:
            # 验证输入
            if not request.text and not request.audio_url:
                return EmotionDetectResponse(
                    success=False,
                    emotions=[],
                    primary_emotion="未知"
                )
            
            # 格式化对话历史
            conversation_context = ""
            if request.conversation_history:
                conversation_context = "\n".join([
                    f"{'用户' if msg.get('role') == 'user' else '助手'}: {msg.get('content', '')}"
                    for msg in request.conversation_history[-5:]  # 最近5条
                ])
            
            logger.info("开始多模态情绪分析...")
            
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
    "primary_emotion": "主要情绪"
}

"""
            
            # 添加对话历史上下文
            if conversation_context:
                analysis_prompt += f"\n对话历史:\n{conversation_context}\n"
            
            # 添加当前文本
            if request.text:
                analysis_prompt += f"\n当前文本: {request.text}\n"
            
            # 构建消息内容
            message_content = [
                {
                    "type": "text",
                    "text": analysis_prompt
                }
            ]
            
            # 如果有音频，添加音频输入
            audio_path = request.audio_url
            if audio_path and os.path.exists(audio_path):
                logger.info(f"处理音频文件: {audio_path}")
                # 读取音频文件
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                file_ext = os.path.splitext(audio_path)[1].lstrip('.')
                
                # 处理格式映射
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
                        "data": f"data:;base64,{audio_base64}",
                        "format": audio_format
                    }
                })
            logger.info(f"message_content: {message_content}")
            
            # 选择模型
            model = config.OMNI_LLM_MODEL if audio_path and os.path.exists(audio_path) else config.TEXT_LLM_MODEL
            logger.info(f"使用模型: {model}")
            
            # 调用 qwen-omni API
            response = self.client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                extra_body={'enable_thinking': config.ENABLE_THINKING},
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS
            )
            
            # 提取分析结果
            analysis_result = response.choices[0].message.content
            logger.info(f"分析完成，原始结果: {analysis_result}")
            
            # 解析结果
            return self._parse_result(analysis_result)
            
        except Exception as e:
            logger.error(f"情绪识别过程出错: {str(e)}", exc_info=True)
            return EmotionDetectResponse(
                success=False,
                emotions=[],
                primary_emotion="未知"
            )
    
    def _parse_result(self, result_text: str) -> EmotionDetectResponse:
        """
        解析 qwen-omni 返回的分析结果
        
        Args:
            result_text: qwen-omni 返回的文本结果
            
        Returns:
            结构化的情绪识别响应
        """
        try:
            # 尝试从markdown代码块中提取JSON
            json_str = self._extract_json(result_text)
            
            if not json_str:
                logger.warning("未找到有效的JSON数据")
                return self._heuristic_parse(result_text)
            
            # 清理JSON字符串
            json_str = self._clean_json(json_str)
            
            # 解析JSON
            result_data = json.loads(json_str)
            
            # 构建情绪结果列表
            emotions = []
            for emotion_data in result_data.get('emotions', []):
                emotions.append(EmotionResult(
                    emotion=emotion_data.get('emotion', '未知'),
                    confidence=float(emotion_data.get('confidence', 0.5)),
                    reason=emotion_data.get('reason', '未提供理由')
                ))
            
            # 如果没有识别出情绪，添加一个默认的
            if not emotions:
                emotions.append(EmotionResult(
                    emotion="平静",
                    confidence=0.5,
                    reason="未检测到明显的情绪信号"
                ))
            
            return EmotionDetectResponse(
                success=True,
                emotions=emotions,
                primary_emotion=result_data.get('primary_emotion', emotions[0].emotion)
            )
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}, 使用启发式解析")
            logger.debug(f"尝试解析的JSON字符串: {json_str if 'json_str' in locals() else 'N/A'}")
            return self._heuristic_parse(result_text)
        except Exception as e:
            logger.error(f"结果解析出错: {e}", exc_info=True)
            return EmotionDetectResponse(
                success=False,
                emotions=[],
                primary_emotion="未知"
            )
    
    def _extract_json(self, text: str) -> str:
        """
        从文本中提取JSON字符串
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            提取出的JSON字符串
        """
        import re
        
        # 尝试从markdown代码块中提取
        json_pattern = r'```(?:json)?\s*\n?([\s\S]*?)\n?```'
        match = re.search(json_pattern, text)
        if match:
            return match.group(1).strip()
        
        # 尝试直接找到JSON对象
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            return text[json_start:json_end]
        
        return ""
    
    def _clean_json(self, json_str: str) -> str:
        """
        清理JSON字符串，移除常见的格式问题
        
        Args:
            json_str: 原始JSON字符串
            
        Returns:
            清理后的JSON字符串
        """
        import re
        
        # 移除单行注释 // ...
        json_str = re.sub(r'//.*?(\n|$)', r'\1', json_str)
        
        # 移除多行注释 /* ... */
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # 移除尾随逗号（在数组或对象末尾）
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # 确保所有键都使用双引号（处理单引号的情况）
        # 这个正则比较复杂，谨慎使用
        # json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        
        return json_str.strip()
    
    def _heuristic_parse(self, result_text: str) -> EmotionDetectResponse:
        """
        启发式解析结果（当JSON解析失败时）
        
        Args:
            result_text: 结果文本
            
        Returns:
            情绪识别响应
        """
        from config import config
        
        # 在文本中查找情绪关键词
        detected_emotions = []
        text_lower = result_text.lower()
        
        for emotion in config.EMOTION_CATEGORIES:
            if emotion in result_text:
                detected_emotions.append(EmotionResult(
                    emotion=emotion,
                    confidence=0.7,
                    reason=f"在分析结果中检测到情绪关键词: {emotion}"
                ))
        
        # 如果没有检测到任何情绪，返回默认情绪
        if not detected_emotions:
            detected_emotions.append(EmotionResult(
                emotion="平静",
                confidence=0.5,
                reason="未检测到明显的情绪信号"
            ))
        
        return EmotionDetectResponse(
            success=True,
            emotions=detected_emotions[:3],  # 最多返回3个情绪
            primary_emotion=detected_emotions[0].emotion
        )

