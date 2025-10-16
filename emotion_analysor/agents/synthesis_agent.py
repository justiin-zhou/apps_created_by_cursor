"""
情绪综合分析Agent - 负责整合多源情绪信息
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from config import config

def create_emotion_synthesis_agent(tools=None) -> Agent:
    """
    创建情绪综合分析Agent
    
    Args:
        tools: 可用的工具列表
        
    Returns:
        配置好的情绪综合分析Agent
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
        role="情绪综合分析师",
        goal="整合文本、音频和对话历史，生成全面准确的情绪识别结果",
        backstory="""
        你是一位资深的心理分析师，擅长整合多维度的信息进行综合判断。
        你能够结合文本内容、音频特征、对话历史和上下文，形成全面的情绪画像。
        你的分析考虑了情绪的复杂性和多样性，能够识别混合情绪和情绪转变。
        你提供的报告清晰、专业，包含主要情绪、次要情绪、置信度和详细理由。
        你的分析结果帮助人们更好地理解自己和他人的情感状态。
        """,
        verbose=True,
        allow_delegation=False,
        tools=tools or [],
        llm=llm,
        max_iter=5,
    )
    
    return agent

