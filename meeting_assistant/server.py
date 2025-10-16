"""
会议助手API服务器
基于FastAPI提供RESTful API接口
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from crew import MeetingAssistantCrew
from models import (
    TranscriptionRequest,
    SummaryRequest,
    QuestionRequest,
    ErrorResponse
)
from config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_AUDIO_FORMATS

# 创建FastAPI应用
app = FastAPI(
    title="会议助手API",
    description="基于CrewAI的智能会议助手，提供会议转写、纪要生成和问答功能",
    version="1.0.0"
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 初始化会议助手Crew
meeting_crew = MeetingAssistantCrew()


@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 返回前端页面"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return {
            "message": "欢迎使用会议助手API",
            "version": "1.0.0",
            "endpoints": {
                "转写会议": "POST /api/transcribe",
                "生成纪要": "POST /api/summary",
                "会议问答": "POST /api/qa",
                "完整处理": "POST /api/process-full",
                "健康检查": "GET /health"
            }
        }

@app.get("/api")
async def api_root():
    """API根路径"""
    return {
        "message": "欢迎使用会议助手API",
        "version": "1.0.0",
        "endpoints": {
            "转写会议": "POST /api/transcribe",
            "生成纪要": "POST /api/summary",
            "会议问答": "POST /api/qa",
            "完整处理": "POST /api/process-full",
            "健康检查": "GET /health"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "meeting-assistant"}


@app.post("/api/transcribe")
async def transcribe_meeting(
    audio_file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    language: str = Form("zh")
):
    """
    转写会议内容
    
    支持两种输入方式：
    1. 上传音频文件
    2. 直接提供文本内容
    """
    try:
        audio_file_path = None
        
        # 处理音频文件
        if audio_file:
            # 验证文件类型
            file_ext = Path(audio_file.filename).suffix.lower()
            if file_ext not in ALLOWED_AUDIO_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的音频格式。支持的格式：{', '.join(ALLOWED_AUDIO_FORMATS)}"
                )
            
            # 保存上传的文件
            audio_file_path = os.path.join(UPLOAD_DIR, audio_file.filename)
            with open(audio_file_path, "wb") as buffer:
                shutil.copyfileobj(audio_file.file, buffer)
        
        # 执行转写
        result = meeting_crew.transcribe_meeting(
            audio_file_path=audio_file_path,
            text_content=text_content
        )
        
        # 清理临时文件
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转写失败: {str(e)}")


@app.post("/api/summary")
async def generate_summary(request: SummaryRequest):
    """
    生成会议纪要
    """
    try:
        result = meeting_crew.generate_summary(request.transcription)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成纪要失败: {str(e)}")


@app.post("/api/qa")
async def answer_question(request: QuestionRequest):
    """
    回答关于会议的问题
    """
    try:
        result = meeting_crew.answer_question(
            meeting_content=request.meeting_content,
            question=request.question
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


@app.post("/api/process-full")
async def process_full_meeting(
    audio_file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    language: str = Form("zh")
):
    """
    完整处理会议：转写 + 生成纪要
    """
    try:
        audio_file_path = None
        
        # 处理音频文件
        if audio_file:
            # 验证文件类型
            file_ext = Path(audio_file.filename).suffix.lower()
            if file_ext not in ALLOWED_AUDIO_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的音频格式。支持的格式：{', '.join(ALLOWED_AUDIO_FORMATS)}"
                )
            
            # 保存上传的文件
            audio_file_path = os.path.join(UPLOAD_DIR, audio_file.filename)
            with open(audio_file_path, "wb") as buffer:
                shutil.copyfileobj(audio_file.file, buffer)
        
        # 执行完整处理
        result = meeting_crew.process_full_meeting(
            audio_file_path=audio_file_path,
            text_content=text_content
        )
        
        # 清理临时文件
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """获取服务统计信息"""
    return {
        "service": "meeting-assistant",
        "agents": {
            "transcription": "会议转写专家",
            "summary": "会议纪要专家",
            "qa": "会议问答专家"
        },
        "capabilities": [
            "音频转文本（支持多种格式）",
            "智能会议纪要生成",
            "基于会议内容的智能问答",
            "完整会议流程处理"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    from config import SERVER_HOST, SERVER_PORT
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║        会议助手 API 服务器启动中...          ║
    ╚══════════════════════════════════════════════╝
    
    🚀 服务地址: http://{SERVER_HOST}:{SERVER_PORT}
    📚 API文档: http://{SERVER_HOST}:{SERVER_PORT}/docs
    📖 ReDoc文档: http://{SERVER_HOST}:{SERVER_PORT}/redoc
    
    支持的功能：
    ✅ 会议音频转写
    ✅ 会议纪要生成
    ✅ 会议内容问答
    ✅ 完整会议流程处理
    """)
    
    uvicorn.run(
        "server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )

