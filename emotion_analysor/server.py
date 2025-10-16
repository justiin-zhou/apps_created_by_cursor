"""
FastAPI服务器 - 情绪识别系统
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from config import config, Config
from models import (
    EmotionDetectRequest,
    EmotionDetectResponse,
    HealthResponse,
    ErrorResponse
)
from crew.emotion_crew import EmotionDetectionCrew

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="情绪识别系统",
    description="基于CrewAI的多Agent情绪识别系统，支持文本和语音输入",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# 初始化Crew（延迟加载）
emotion_crew: Optional[EmotionDetectionCrew] = None

def get_emotion_crew() -> EmotionDetectionCrew:
    """获取或创建EmotionDetectionCrew实例"""
    global emotion_crew
    if emotion_crew is None:
        logger.info("初始化 EmotionDetectionCrew...")
        emotion_crew = EmotionDetectionCrew()
    return emotion_crew

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    try:
        # 验证配置
        Config.validate()
        logger.info("配置验证通过")
        
        # 确保上传目录存在
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        logger.info(f"上传目录: {config.UPLOAD_DIR}")
        
        logger.info("服务器启动成功")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页"""
    index_path = os.path.join(static_path, "index.html")
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        logger.error(f"读取index.html失败: {e}")
        return HTMLResponse(
            content="<h1>错误: 无法加载前端页面</h1>",
            status_code=500
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )

@app.post("/api/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    上传音频文件
    
    Args:
        file: 上传的音频文件
        
    Returns:
        包含文件路径的响应
    """
    try:
        # 检查文件扩展名
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in config.ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}. 支持的格式: {', '.join(config.ALLOWED_AUDIO_EXTENSIONS)}"
            )
        
        # 生成唯一文件名
        import uuid
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(config.UPLOAD_DIR, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > config.MAX_FILE_SIZE:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"文件过大: {file_size} 字节. 最大允许: {config.MAX_FILE_SIZE} 字节"
            )
        
        logger.info(f"文件上传成功: {unique_filename}, 大小: {file_size} 字节")
        
        return {
            "success": True,
            "filename": unique_filename,
            "file_path": file_path,
            "file_size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@app.post("/api/emotion_detect", response_model=EmotionDetectResponse)
async def detect_emotion(request: EmotionDetectRequest):
    """
    情绪识别端点
    
    Args:
        request: 情绪识别请求
        
    Returns:
        情绪识别结果
    """
    try:
        logger.info(f"收到情绪识别请求 - 文本: {request.text[:50] if request.text else None}, 音频: {request.audio_url}")
        
        # 验证输入
        if not request.text and not request.audio_url:
            raise HTTPException(
                status_code=400,
                detail="请提供文本或音频输入"
            )
        
        # 如果有音频URL，检查文件是否存在
        if request.audio_url:
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(request.audio_url):
                audio_path = os.path.join(config.UPLOAD_DIR, os.path.basename(request.audio_url))
            else:
                audio_path = request.audio_url
            
            if not os.path.exists(audio_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"音频文件不存在: {request.audio_url}"
                )
            
            # 更新请求中的音频路径为绝对路径
            request.audio_url = audio_path
        
        # 获取Crew实例
        crew = get_emotion_crew()
        
        # 执行情绪识别
        logger.info("开始执行情绪识别...")
        result = crew.analyze_emotion(request)
        
        logger.info(f"情绪识别完成 - 主要情绪: {result.primary_emotion}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"情绪识别失败: {e}", exc_info=True)
        return EmotionDetectResponse(
            success=False,
            emotions=[],
            primary_emotion="未知",
            analysis=f"情绪识别过程出错: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"服务器内部错误: {str(exc)}"
        }
    )

def main():
    """启动服务器"""
    logger.info(f"启动服务器 - Host: {config.HOST}, Port: {config.PORT}")
    uvicorn.run(
        "server:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main()

