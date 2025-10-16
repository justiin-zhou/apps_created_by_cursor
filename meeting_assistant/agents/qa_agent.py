"""
会议问答Agent
负责基于会议内容回答问题
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from config import API_KEY, API_BASE_URL, MODEL_NAME


def create_qa_agent():
    """
    创建会议问答Agent
    """
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=API_BASE_URL,
        temperature=0.2
    )
    
    agent = Agent(
        role="会议内容问答专家",
        goal="准确回答关于会议内容的问题，提供详细且有依据的答案",
        backstory="""你是一位会议内容分析专家，擅长深入理解会议讨论的内容和上下文。
        你能够根据会议记录准确回答各种问题，包括具体细节、决策背景、讨论要点等。
        你的回答总是基于实际的会议内容，不会编造信息。当遇到会议中未涉及的问题时，
        你会明确告知用户。你特别擅长：
        - 回忆会议中的具体讨论内容
        - 解释决策的背景和原因
        - 提供相关的上下文信息
        - 引用会议中的具体表述
        """,
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return agent

