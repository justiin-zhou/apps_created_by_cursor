"""
情绪识别任务定义
"""
from crewai import Task
from typing import List, Dict, Optional
from config import config

class EmotionDetectionTasks:
    """情绪识别任务集合"""
    
    @staticmethod
    def analyze_text_emotion_task(
        agent,
        text: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Task:
        """
        创建文本情绪分析任务
        
        Args:
            agent: 执行任务的Agent
            text: 需要分析的文本
            conversation_history: 对话历史
            
        Returns:
            配置好的Task对象
        """
        # 构建上下文
        context_str = ""
        if conversation_history:
            context_str = "对话历史:\n"
            for msg in conversation_history[-5:]:  # 只取最近5条
                role = "用户" if msg.get("role") == "user" else "助手"
                context_str += f"{role}: {msg.get('content', '')}\n"
        
        description = f"""
        分析以下文本中的情绪:
        
        {context_str}
        
        当前文本: {text}
        
        请识别文本中的情绪，可以包含多种情绪。
        
        可选的情绪类型包括但不限于:
        {', '.join(config.EMOTION_CATEGORIES)}
        
        请分析:
        1. 识别出的所有情绪类型
        2. 每种情绪的强度（0-1之间的置信度）
        3. 识别该情绪的理由
        4. 结合对话历史的上下文分析
        
        请以结构化的方式输出分析结果。
        """
        
        expected_output = """
        文本情绪分析报告，包含:
        - 识别出的情绪列表（每个情绪包含类型、置信度、理由）
        - 情绪分析的依据（具体的词语、语气、上下文等）
        - 建议的主要情绪
        """
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
        )
    
    @staticmethod
    def analyze_audio_emotion_task(
        agent,
        audio_path: str,
        text_content: Optional[str] = None
    ) -> Task:
        """
        创建音频情绪分析任务
        
        Args:
            agent: 执行任务的Agent
            audio_path: 音频文件路径
            text_content: 音频对应的文本内容（如果有）
            
        Returns:
            配置好的Task对象
        """
        text_info = f"\n音频文本内容: {text_content}" if text_content else ""
        
        description = f"""
        分析音频文件中的情绪特征:
        
        音频文件路径: {audio_path}{text_info}
        
        请使用音频处理工具分析音频文件，并识别以下方面:
        1. 语音的语调特征（高昂/低沉/平稳）
        2. 语速特征（快速/正常/缓慢）
        3. 音量变化
        4. 停顿和节奏
        5. 语音中的情绪信号
        
        基于这些特征，判断说话者可能的情绪状态。
        
        可选的情绪类型包括:
        {', '.join(config.EMOTION_CATEGORIES)}
        """
        
        expected_output = """
        音频情绪分析报告，包含:
        - 识别出的情绪列表
        - 音频特征描述（语调、语速、音量等）
        - 情绪判断的声学依据
        """
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
        )
    
    @staticmethod
    def synthesize_emotion_task(
        agent,
        text_analysis: Optional[str] = None,
        audio_analysis: Optional[str] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> Task:
        """
        创建情绪综合分析任务
        
        Args:
            agent: 执行任务的Agent
            text_analysis: 文本分析结果
            audio_analysis: 音频分析结果
            conversation_history: 对话历史
            
        Returns:
            配置好的Task对象
        """
        context_items = []
        
        if text_analysis:
            context_items.append(f"文本分析结果:\n{text_analysis}")
        
        if audio_analysis:
            context_items.append(f"音频分析结果:\n{audio_analysis}")
        
        if conversation_history:
            history_str = "对话历史:\n"
            for msg in conversation_history[-5:]:
                role = "用户" if msg.get("role") == "user" else "助手"
                history_str += f"{role}: {msg.get('content', '')}\n"
            context_items.append(history_str)
        
        context = "\n\n".join(context_items)
        
        description = f"""
        综合以下所有信息，生成最终的情绪识别结果:
        
        {context}
        
        请整合以上信息，输出最终的情绪识别结果。需要包含:
        
        1. **识别出的所有情绪**: 列出所有检测到的情绪，每个情绪包含:
           - emotion: 情绪类型（中文）
           - confidence: 置信度（0.0-1.0之间的浮点数）
           - reason: 识别该情绪的具体理由（50字以内）
        
        2. **主要情绪**: 选择置信度最高的情绪作为主要情绪
        
        3. **综合分析**: 200字以内的综合情绪分析报告
        
        请确保:
        - 至少识别出1-3种情绪
        - 置信度要合理，反映情绪的明确程度
        - 理由要具体，基于实际的文本或音频特征
        - 综合分析要考虑所有维度的信息
        
        输出格式必须是有效的JSON，结构如下:
        {{
            "emotions": [
                {{
                    "emotion": "情绪类型",
                    "confidence": 0.85,
                    "reason": "识别理由"
                }}
            ],
            "primary_emotion": "主要情绪",
            "analysis": "综合分析文本"
        }}
        """
        
        expected_output = """
        一个完整的JSON格式情绪识别报告，包含:
        - emotions: 情绪列表数组，每项包含emotion、confidence、reason
        - primary_emotion: 字符串，主要情绪
        - analysis: 字符串，综合分析
        
        必须是有效的JSON格式，可以直接解析。
        """
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
        )

