"""
情绪分析Agent - 使用 qwen-omni 多模态分析情绪
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from config import config

def create_emotion_synthesis_agent(tools=None) -> Agent:
    """
    创建情绪分析Agent
    
    Args:
        tools: 可用的工具列表（包含 AudioProcessorTool）
        
    Returns:
        配置好的情绪分析Agent
    """
    # 配置LLM - 使用 qwen-omni
    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.DASHSCOPE_API_BASE,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
    )
    
    agent = Agent(
        role="专业情绪分析师",
        goal="综合分析用户的文本、语音和对话历史，准确识别情绪状态",
        backstory="""
        你是一位经验丰富的情绪分析专家和心理学家。
        你擅长使用多模态信息（文本、语音、对话历史）进行情绪识别。
        你可以使用"多模态情绪分析工具"来分析用户输入，该工具会：
        - 分析文本内容中的情绪表达
        - 分析语音中的语调、语速、音量等声学特征
        - 结合对话历史理解情绪变化
        
        你的任务是调用工具获取分析结果，然后确保结果是标准的JSON格式。
        如果工具返回的结果不是JSON格式，你需要将其转换为标准JSON格式：
        {
            "emotions": [{"emotion": "情绪", "confidence": 0.85, "reason": "理由"}],
            "primary_emotion": "主要情绪",
            "analysis": "综合分析"
        }
        """,
        verbose=True,
        allow_delegation=False,
        tools=tools or [],
        llm=llm,
        max_iter=10,
    )
    
    return agent

