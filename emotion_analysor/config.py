"""
配置文件 - 支持qwen-omni模型
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # API配置
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_API_BASE = os.getenv("DASHSCOPE_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # 模型配置
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-omni")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    
    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # 文件上传配置
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
    
    # 情绪分类配置
    EMOTION_CATEGORIES = [
        "开心", "快乐", "兴奋", "满足",
        "悲伤", "难过", "失落", "沮丧",
        "愤怒", "生气", "烦躁", "不满",
        "焦虑", "担心", "紧张", "恐惧",
        "惊讶", "震惊", "困惑",
        "平静", "放松", "淡定",
        "厌恶", "反感", "无聊",
        "期待", "希望", "好奇",
        "感激", "感动", "温暖",
        "孤独", "寂寞", "无助",
        "自信", "自豪", "骄傲",
        "羞愧", "内疚", "尴尬",
        "疲惫", "困倦", "无力"
    ]
    
    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        if not cls.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY 未设置，请在.env文件中配置")
        
        # 确保上传目录存在
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
        
        return True

# 配置实例
config = Config()

