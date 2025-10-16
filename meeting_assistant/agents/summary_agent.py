"""
会议纪要Agent
负责生成会议摘要和关键要点
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from config import API_KEY, API_BASE_URL, MODEL_NAME


def create_summary_agent():
    """
    创建会议纪要Agent
    """
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=API_BASE_URL,
        temperature=0.3
    )
    
    agent = Agent(
        role="会议纪要专家",
        goal="生成清晰、简洁、结构化的会议纪要，提取关键决策和行动项",
        backstory="""你是一位专业的会议纪要专家，拥有多年的会议记录和总结经验。
        你擅长从大量会议内容中提取核心信息，识别关键决策、行动项和重要讨论点。
        你的纪要总是结构清晰、条理分明，能够帮助参会者快速回顾会议内容。
        你特别注重识别：会议目标、主要讨论点、决策事项、行动项（包括负责人和
        截止日期）、以及下一步计划。""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return agent

