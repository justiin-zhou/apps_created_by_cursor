"""
任务模块
"""
from .meeting_tasks import (
    create_transcription_task,
    create_summary_task,
    create_qa_task
)

__all__ = [
    'create_transcription_task',
    'create_summary_task',
    'create_qa_task'
]

