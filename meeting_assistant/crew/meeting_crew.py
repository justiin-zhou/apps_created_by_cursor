"""
会议助手Crew
整合所有agents和tasks
"""
from crewai import Crew, Process
from agents import create_transcription_agent, create_summary_agent, create_qa_agent
from tasks import create_transcription_task, create_summary_task, create_qa_task
from tools import TranscriptionTool


class MeetingAssistantCrew:
    """
    会议助手Crew类
    协调所有agents完成会议相关任务
    """
    
    def __init__(self):
        # 创建agents
        self.transcription_agent = create_transcription_agent()
        self.summary_agent = create_summary_agent()
        self.qa_agent = create_qa_agent()
        
        # 创建工具
        self.transcription_tool = TranscriptionTool()
    
    def transcribe_meeting(self, audio_file_path: str = None, text_content: str = None) -> dict:
        """
        转写会议内容
        
        Args:
            audio_file_path: 音频文件路径（可选）
            text_content: 文本内容（可选）
            
        Returns:
            转写结果
        """
        # 获取原始内容
        if audio_file_path:
            transcription_result = self.transcription_tool.transcribe_audio(audio_file_path)
            if "error" in transcription_result:
                return transcription_result
            raw_content = transcription_result["text"]
        elif text_content:
            raw_content = text_content
        else:
            return {"error": "必须提供音频文件或文本内容"}
        
        # 创建任务
        task = create_transcription_task(self.transcription_agent, raw_content)
        
        # 创建crew并执行
        crew = Crew(
            agents=[self.transcription_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "raw_transcription": raw_content,
            "formatted_transcription": str(result),
            "status": "success"
        }
    
    def generate_summary(self, transcription: str) -> dict:
        """
        生成会议纪要
        
        Args:
            transcription: 会议转写文本
            
        Returns:
            会议纪要
        """
        # 创建任务
        task = create_summary_task(self.summary_agent, transcription)
        
        # 创建crew并执行
        crew = Crew(
            agents=[self.summary_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "summary": str(result),
            "status": "success"
        }
    
    def answer_question(self, meeting_content: str, question: str) -> dict:
        """
        回答关于会议的问题
        
        Args:
            meeting_content: 会议内容（转写文本或纪要）
            question: 问题
            
        Returns:
            答案
        """
        # 创建任务
        task = create_qa_task(self.qa_agent, meeting_content, question)
        
        # 创建crew并执行
        crew = Crew(
            agents=[self.qa_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "question": question,
            "answer": str(result),
            "status": "success"
        }
    
    def process_full_meeting(self, audio_file_path: str = None, text_content: str = None) -> dict:
        """
        完整处理会议：转写 + 生成纪要
        
        Args:
            audio_file_path: 音频文件路径（可选）
            text_content: 文本内容（可选）
            
        Returns:
            完整的会议处理结果
        """
        # 步骤1: 转写
        transcription_result = self.transcribe_meeting(audio_file_path, text_content)
        if "error" in transcription_result:
            return transcription_result
        
        # 步骤2: 生成纪要
        summary_result = self.generate_summary(
            transcription_result["formatted_transcription"]
        )
        
        return {
            "transcription": transcription_result,
            "summary": summary_result,
            "status": "success"
        }

