"""
音频分析Agent - 负责音频情绪分析
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from config import config

def create_audio_analysis_agent(tools=None) -> Agent:
    """
    创建音频分析Agent
    
    Args:
        tools: 可用的工具列表
        
    Returns:
        配置好的音频分析Agent
    """
    # 配置LLM - 使用qwen-omni支持音频理解
    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.DASHSCOPE_API_BASE,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
    )
    
    agent = Agent(
        role="音频情绪分析专家",
        goal="从音频中提取情绪特征，分析语音中的情感信号",
        backstory="""
        你是一位专业的语音情感分析专家，能够通过音频特征（如语调、语速、音量、停顿等）
        识别说话者的情绪状态。你熟悉各种情绪在语音中的表现形式，能够捕捉微妙的情感变化。
        你的分析综合考虑了声学特征和语言内容，提供全面的情绪评估。
        """,
        verbose=True,
        allow_delegation=False,
        tools=tools or [],
        llm=llm,
        max_iter=5,
    )
    
    return agent

