"""
情绪识别Crew - 协调多个Agent完成情绪识别任务
"""
from crewai import Crew, Process
from typing import Dict, List, Optional, Any
import json
import logging

from agents.emotion_agent import create_emotion_detection_agent
from agents.audio_agent import create_audio_analysis_agent
from agents.synthesis_agent import create_emotion_synthesis_agent
from tasks.emotion_tasks import EmotionDetectionTasks
from tools.audio_processor import AudioProcessorTool
from tools.emotion_analyzer import EmotionAnalyzerTool
from models import EmotionDetectRequest, EmotionDetectResponse, EmotionResult

logger = logging.getLogger(__name__)

class EmotionDetectionCrew:
    """情绪识别Crew - Multi-Agent协作系统"""
    
    def __init__(self):
        """初始化Crew"""
        # 初始化工具
        self.audio_tool = AudioProcessorTool()
        self.emotion_tool = EmotionAnalyzerTool()
        
        # 初始化Agents
        self.emotion_agent = create_emotion_detection_agent(
            tools=[self.emotion_tool]
        )
        self.audio_agent = create_audio_analysis_agent(
            tools=[self.audio_tool]
        )
        self.synthesis_agent = create_emotion_synthesis_agent()
        
        logger.info("EmotionDetectionCrew 初始化完成")
    
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
            tasks = []
            task_results = {}
            
            # 1. 如果有文本，创建文本分析任务
            if request.text:
                logger.info(f"创建文本分析任务: {request.text[:50]}...")
                text_task = EmotionDetectionTasks.analyze_text_emotion_task(
                    agent=self.emotion_agent,
                    text=request.text,
                    conversation_history=request.conversation_history
                )
                tasks.append(text_task)
            
            # 2. 如果有音频，创建音频分析任务
            if request.audio_url:
                logger.info(f"创建音频分析任务: {request.audio_url}")
                audio_task = EmotionDetectionTasks.analyze_audio_emotion_task(
                    agent=self.audio_agent,
                    audio_path=request.audio_url,
                    text_content=request.text
                )
                tasks.append(audio_task)
            
            # 如果既没有文本也没有音频，返回错误
            if not tasks:
                return EmotionDetectResponse(
                    success=False,
                    emotions=[],
                    primary_emotion="未知",
                    analysis="错误: 请提供文本或音频输入"
                )
            
            # 3. 执行分析任务（顺序执行）
            if len(tasks) == 1:
                # 只有一个任务，直接执行
                crew = Crew(
                    agents=[tasks[0].agent],
                    tasks=[tasks[0]],
                    process=Process.sequential,
                    verbose=True
                )
                result = crew.kickoff()
                if request.text and not request.audio_url:
                    task_results['text_analysis'] = str(result)
                else:
                    task_results['audio_analysis'] = str(result)
            else:
                # 有多个任务，分别执行
                for i, task in enumerate(tasks):
                    crew = Crew(
                        agents=[task.agent],
                        tasks=[task],
                        process=Process.sequential,
                        verbose=True
                    )
                    result = crew.kickoff()
                    if i == 0 and request.text:
                        task_results['text_analysis'] = str(result)
                    elif request.audio_url:
                        task_results['audio_analysis'] = str(result)
            
            # 4. 创建综合分析任务
            logger.info("创建综合分析任务")
            synthesis_task = EmotionDetectionTasks.synthesize_emotion_task(
                agent=self.synthesis_agent,
                text_analysis=task_results.get('text_analysis'),
                audio_analysis=task_results.get('audio_analysis'),
                conversation_history=request.conversation_history
            )
            
            # 5. 执行综合分析
            synthesis_crew = Crew(
                agents=[self.synthesis_agent],
                tasks=[synthesis_task],
                process=Process.sequential,
                verbose=True
            )
            
            synthesis_result = synthesis_crew.kickoff()
            logger.info(f"综合分析结果: {synthesis_result}")
            
            # 6. 解析结果
            return self._parse_result(str(synthesis_result))
            
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

