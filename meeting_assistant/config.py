"""
配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# AI 模型配置
# 支持 DeepSeek 和 OpenAI
USE_DEEPSEEK = os.getenv("USE_DEEPSEEK", "true").lower() == "true"

if USE_DEEPSEEK:
    # DeepSeek 配置
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    API_BASE_URL = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
else:
    # OpenAI 配置（备用）
    API_KEY = os.getenv("OPENAI_API_KEY")
    API_BASE_URL = "https://api.openai.com/v1"
    MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")

# 语音识别配置
# 如果使用 DeepSeek，语音识别可以使用阿里云、腾讯云等国内服务
# 这里保留 OpenAI Whisper 作为选项
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY", API_KEY)
WHISPER_API_BASE = os.getenv("WHISPER_API_BASE", "https://api.openai.com/v1")

# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

# 文件上传配置
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]

