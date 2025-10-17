"""
数据记录模块 - 将每次分析的数据存储到本地文件
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataLogger:
    """数据记录器 - 记录每次情绪分析的详细信息"""
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        初始化数据记录器
        
        Args:
            log_dir: 日志存储目录，默认使用配置中的目录
        """
        if log_dir is None:
            from config import config
            log_dir = config.DATA_LOG_DIR
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 使用日期作为文件名，便于管理
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"emotion_analysis_{today}.jsonl"
        
        logger.info(f"数据记录器初始化完成，日志文件: {self.log_file}")
    
    def log_analysis(
        self,
        timestamp: str,
        text_input: Optional[str],
        audio_input: Optional[str],
        conversation_history: List[Dict[str, str]],
        analysis_result: Dict[str, Any],
        processing_time: float,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        记录一次分析的完整数据
        
        Args:
            timestamp: 时间戳
            text_input: 当前文本输入
            audio_input: 当前语音输入文件路径
            conversation_history: 对话历史
            analysis_result: 识别结果
            processing_time: 处理耗时（秒）
            success: 是否成功
            error_message: 错误信息（如果有）
        """
        try:
            # 构建记录数据
            log_entry = {
                "timestamp": timestamp,
                "inputs": {
                    "text": text_input,
                    "audio_path": audio_input,
                    "conversation_history": conversation_history
                },
                "result": analysis_result,
                "processing_time_seconds": round(processing_time, 3),
                "success": success,
                "error": error_message
            }
            
            # 追加到文件（JSONL格式，每行一个JSON对象）
            with open(self.log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write('\n')
            
            logger.debug(f"数据记录成功: {timestamp}")
            
        except Exception as e:
            logger.error(f"数据记录失败: {str(e)}", exc_info=True)
    
    def get_logs(self, date: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        读取日志记录
        
        Args:
            date: 日期 (YYYY-MM-DD)，默认为今天
            limit: 最多返回的记录数
            
        Returns:
            日志记录列表
        """
        try:
            if date:
                log_file = self.log_dir / f"emotion_analysis_{date}.jsonl"
            else:
                log_file = self.log_file
            
            if not log_file.exists():
                return []
            
            logs = []
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
                        if len(logs) >= limit:
                            break
            
            return logs
            
        except Exception as e:
            logger.error(f"读取日志失败: {str(e)}", exc_info=True)
            return []
    
    def get_statistics(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            date: 日期 (YYYY-MM-DD)，默认为今天
            
        Returns:
            统计信息
        """
        try:
            logs = self.get_logs(date, limit=100000)
            
            if not logs:
                return {
                    "total_count": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "avg_processing_time": 0,
                    "emotion_distribution": {}
                }
            
            success_count = sum(1 for log in logs if log.get('success'))
            error_count = len(logs) - success_count
            
            processing_times = [log.get('processing_time_seconds', 0) for log in logs]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # 统计情绪分布
            emotion_distribution = {}
            for log in logs:
                if log.get('success') and log.get('result'):
                    primary_emotion = log['result'].get('primary_emotion')
                    if primary_emotion:
                        emotion_distribution[primary_emotion] = emotion_distribution.get(primary_emotion, 0) + 1
            
            return {
                "total_count": len(logs),
                "success_count": success_count,
                "error_count": error_count,
                "avg_processing_time": round(avg_processing_time, 3),
                "emotion_distribution": emotion_distribution
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}", exc_info=True)
            return {}

# 全局数据记录器实例
_data_logger: Optional[DataLogger] = None

def get_data_logger() -> DataLogger:
    """获取全局数据记录器实例"""
    global _data_logger
    if _data_logger is None:
        _data_logger = DataLogger()
    return _data_logger

