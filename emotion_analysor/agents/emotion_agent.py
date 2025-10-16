"""
情绪识别Agent - 负责文本情绪分析
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from config import config

def create_emotion_detection_agent(tools=None) -> Agent:
    """
    创建情绪识别Agent
    
    Args:
        tools: 可用的工具列表
        
    Returns:
        配置好的情绪识别Agent
    """
    # 配置LLM
    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.DASHSCOPE_API_BASE,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
    )
    
    agent = Agent(
        role="情绪识别专家",
        goal="准确识别用户文本中的情绪类型，提供多维度的情绪分析",
        backstory="""
        你是一位经验丰富的心理学家和情绪识别专家，擅长通过文本分析人类的情绪状态。
        你能够识别细微的情绪变化，理解情绪背后的原因，并提供专业的情绪分析报告。
        你的分析既科学严谨，又富有同理心，能够准确捕捉用户的真实情感。
        """,
        verbose=True,
        allow_delegation=False,
        tools=tools or [],
        llm=llm,
        max_iter=5,
    )
    
    return agent

