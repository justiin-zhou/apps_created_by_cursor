"""
会议相关任务定义
"""
from crewai import Task


def create_transcription_task(agent, meeting_content: str):
    """
    创建转写任务
    """
    task = Task(
        description=f"""
        处理以下会议内容，生成清晰、结构化的会议转写记录：
        
        会议内容：
        {meeting_content}
        
        请确保：
        1. 保持内容的完整性和准确性
        2. 识别并标注不同的说话者（如果可能）
        3. 保留重要的时间信息
        4. 修正明显的语音识别错误
        5. 使用合适的段落和标点符号
        """,
        expected_output="""
        一个格式化的会议转写文本，包括：
        - 清晰的段落划分
        - 说话者标识（如有）
        - 关键时间点标注
        - 纠正后的准确文本
        """,
        agent=agent
    )
    return task


def create_summary_task(agent, transcription: str):
    """
    创建会议纪要任务
    """
    task = Task(
        description=f"""
        基于以下会议转写内容，生成一份全面的会议纪要：
        
        会议转写：
        {transcription}
        
        请包含以下内容：
        1. **会议概览**：会议主题、时间、参与者
        2. **主要讨论点**：列出所有重要讨论议题
        3. **关键决策**：记录所有做出的决定
        4. **行动项**：列出所有待办事项，包括负责人和截止日期（如有提及）
        5. **下一步计划**：后续安排和跟进事项
        6. **其他重要信息**：任何值得注意的内容
        """,
        expected_output="""
        一份结构化的会议纪要，包括：
        - 会议概览
        - 主要讨论点（要点列表）
        - 关键决策（编号列表）
        - 行动项（表格形式：任务、负责人、截止日期）
        - 下一步计划
        - 其他重要信息
        
        格式清晰，易于阅读和存档。
        """,
        agent=agent
    )
    return task


def create_qa_task(agent, meeting_content: str, question: str):
    """
    创建问答任务
    """
    task = Task(
        description=f"""
        基于以下会议内容回答问题：
        
        会议内容：
        {meeting_content}
        
        问题：{question}
        
        请提供：
        1. 直接回答问题
        """,
        expected_output="""
        一个详细的答案，包括：
        - 直接回答
        """,
        agent=agent
    )
    return task

