"""
Agent模块初始化
"""
from .emotion_agent import create_emotion_detection_agent
from .audio_agent import create_audio_analysis_agent
from .synthesis_agent import create_emotion_synthesis_agent

__all__ = [
    'create_emotion_detection_agent',
    'create_audio_analysis_agent',
    'create_emotion_synthesis_agent'
]

