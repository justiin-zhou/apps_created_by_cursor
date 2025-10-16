"""
情绪分析工具
"""
from crewai.tools import BaseTool
from typing import Type, List, Dict, ClassVar
from pydantic import BaseModel, Field
import json

class EmotionAnalyzerInput(BaseModel):
    """情绪分析工具输入模型"""
    text: str = Field(..., description="需要分析的文本内容")
    context: str = Field(default="", description="上下文信息")

class EmotionAnalyzerTool(BaseTool):
    """情绪分析工具 - 基于文本和上下文分析情绪"""
    
    name: str = "情绪分析工具"
    description: str = (
        "分析文本内容中的情绪信息，识别多种情绪类型及其强度。"
        "输入参数: text (文本内容), context (上下文)"
        "返回: 情绪分析结果，包含情绪类型、置信度和理由"
    )
    args_schema: Type[BaseModel] = EmotionAnalyzerInput
    
    # 情绪关键词映射 - 使用 ClassVar 标注
    EMOTION_KEYWORDS: ClassVar[Dict[str, List[str]]] = {
        "开心": ["开心", "高兴", "快乐", "愉快", "欢乐", "喜悦", "哈哈", "嘻嘻"],
        "兴奋": ["兴奋", "激动", "澎湃", "热血", "振奋"],
        "悲伤": ["悲伤", "难过", "伤心", "心痛", "哭", "泪"],
        "愤怒": ["愤怒", "生气", "气愤", "暴怒", "火大"],
        "焦虑": ["焦虑", "担心", "忧虑", "不安", "紧张"],
        "惊讶": ["惊讶", "震惊", "吃惊", "意外", "天啊"],
        "厌恶": ["厌恶", "恶心", "讨厌", "反感"],
        "恐惧": ["恐惧", "害怕", "惊恐", "可怕"],
        "平静": ["平静", "淡定", "冷静", "安静"],
        "期待": ["期待", "希望", "盼望", "憧憬"],
        "感激": ["感谢", "感激", "感恩", "谢谢"],
        "失落": ["失落", "失望", "沮丧", "郁闷"],
    }
    
    def _run(self, text: str, context: str = "") -> str:
        """
        执行情绪分析
        
        Args:
            text: 需要分析的文本
            context: 上下文信息
            
        Returns:
            情绪分析结果的JSON字符串
        """
        try:
            emotions_found = []
            
            # 简单的关键词匹配（实际应用中会使用更复杂的NLP技术）
            text_lower = text.lower()
            for emotion, keywords in self.EMOTION_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        emotions_found.append({
                            "emotion": emotion,
                            "confidence": 0.8,
                            "keyword": keyword
                        })
                        break
            
            # 如果没有找到明显的情绪关键词，返回提示
            if not emotions_found:
                result = {
                    "status": "需要深度分析",
                    "text": text,
                    "context": context,
                    "preliminary_emotions": [],
                    "note": "未检测到明显情绪关键词，需要AI进行深度语义分析"
                }
            else:
                result = {
                    "status": "初步分析完成",
                    "text": text,
                    "context": context,
                    "preliminary_emotions": emotions_found,
                    "note": f"检测到 {len(emotions_found)} 个初步情绪信号"
                }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            }, ensure_ascii=False)
    
    async def _arun(self, text: str, context: str = "") -> str:
        """异步执行"""
        return self._run(text, context)

