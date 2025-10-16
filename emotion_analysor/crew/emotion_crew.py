"""
情绪识别Crew - 使用单一 Agent 完成多模态情绪识别
"""
from crewai import Crew, Process, Task
from typing import Dict, List, Optional, Any
import json
import logging

from agents.synthesis_agent import create_emotion_synthesis_agent
from tools.audio_processor import AudioProcessorTool
from models import EmotionDetectRequest, EmotionDetectResponse, EmotionResult

logger = logging.getLogger(__name__)

class EmotionDetectionCrew:
    """情绪识别Crew - 单Agent多模态分析系统"""
    
    def __init__(self):
        """初始化Crew"""
        # 初始化多模态分析工具
        self.multimodal_tool = AudioProcessorTool()
        
        # 初始化情绪分析Agent（配备多模态工具）
        self.emotion_agent = create_emotion_synthesis_agent(
            tools=[self.multimodal_tool]
        )
        
        logger.info("EmotionDetectionCrew 初始化完成（单Agent架构）")
    
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
                    primary_emotion="未知",
                    analysis="错误: 请提供文本或音频输入"
                )
            
            # 格式化对话历史
            conversation_context = ""
            if request.conversation_history:
                conversation_context = "\n".join([
                    f"{'用户' if msg.get('role') == 'user' else '助手'}: {msg.get('content', '')}"
                    for msg in request.conversation_history[-5:]  # 最近5条
                ])
            
            # 构建任务描述
            task_description = f"""
请使用多模态情绪分析工具分析用户的情绪状态。

输入信息：
- 文本内容: {request.text or '无'}
- 音频文件: {request.audio_url or '无'}
- 对话历史: {conversation_context or '无'}

请调用"多模态情绪分析工具"，传入以下参数：
- audio_path: "{request.audio_url or ''}"
- text: "{request.text or ''}"
- conversation_history: "{conversation_context}"

工具会返回JSON格式的分析结果。请确保最终输出是有效的JSON格式：
{{
    "emotions": [
        {{
            "emotion": "情绪类型",
            "confidence": 0.85,
            "reason": "识别理由"
        }}
    ],
    "primary_emotion": "主要情绪",
    "analysis": "综合分析"
}}
"""
            
            # 创建任务
            task = Task(
                description=task_description,
                expected_output="包含emotions数组、primary_emotion和analysis的JSON格式结果",
                agent=self.emotion_agent,
            )
            
            # 创建并执行Crew
            logger.info("开始多模态情绪分析...")
            crew = Crew(
                agents=[self.emotion_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            logger.info(f"分析完成，结果: {result}")
            
            # 解析结果
            return self._parse_result(str(result))
            
        except Exception as e:
            logger.error(f"情绪识别过程出错: {str(e)}", exc_info=True)
            return EmotionDetectResponse(
                success=False,
                emotions=[],
                primary_emotion="未知",
                analysis=f"分析过程出错: {str(e)}"
            )
    
    def _parse_result(self, result_text: str) -> EmotionDetectResponse:
        """
        解析Crew执行结果
        
        Args:
            result_text: Crew返回的文本结果
            
        Returns:
            结构化的情绪识别响应
        """
        try:
            # 尝试从结果中提取JSON
            # 结果可能包含额外的文本，需要找到JSON部分
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
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
                    primary_emotion=result_data.get('primary_emotion', emotions[0].emotion),
                    analysis=result_data.get('analysis', '情绪分析完成')
                )
            else:
                # 如果没有找到JSON，使用启发式方法解析
                return self._heuristic_parse(result_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}, 使用启发式解析")
            return self._heuristic_parse(result_text)
        except Exception as e:
            logger.error(f"结果解析出错: {e}", exc_info=True)
            return EmotionDetectResponse(
                success=False,
                emotions=[],
                primary_emotion="未知",
                analysis=f"结果解析失败: {str(e)}"
            )
    
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
            primary_emotion=detected_emotions[0].emotion,
            analysis=result_text[:300]  # 取前300字符作为分析
        )

