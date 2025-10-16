"""
会议转写Agent
负责将音频文件转换为文本
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from config import API_KEY, API_BASE_URL, MODEL_NAME


def create_transcription_agent():
    """
    创建会议转写Agent
    """
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=API_BASE_URL,
        temperature=0.1
    )
    
    agent = Agent(
        role="会议转写专家",
        goal="准确地将会议音频转换为结构化的文本记录",
        backstory="""你是一位经验丰富的会议转写专家，擅长将音频内容转换为清晰、
        准确的文字记录。你能够识别不同的说话者，正确标注时间戳，并保持会议内容
        的完整性和准确性。你对语音识别技术有深入的了解，能够处理各种口音和
        背景噪音的情况。""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return agent

