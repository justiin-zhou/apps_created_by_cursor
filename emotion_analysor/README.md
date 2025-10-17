# 🎭 智能情绪识别系统

基于 CrewAI 多 Agent 协作的智能情绪识别系统，支持文本和语音输入，采用 Qwen-Omni 模型进行情绪分析。

## ✨ 核心功能

- 🎯 **多维情绪识别**: 识别日常生活中的多种情绪类型（开心、悲伤、愤怒、焦虑等）
- 🎙️ **语音分析**: 支持音频文件上传，分析语音中的情感信号
- 💬 **对话历史**: 结合对话上下文进行更准确的情绪判断
- 🤖 **Multi-Agent 架构**: 三个专业 Agent 协作完成情绪识别任务
- 🎨 **现代化 UI**: 紫蓝渐变主题，响应式设计，支持拖拽上传

## 🏗️ 系统架构

### Multi-Agent 协作系统

```
┌─────────────────────────────────────────────────┐
│            EmotionDetectionCrew                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────┐  ┌────────────────────┐ │
│  │ Emotion Agent    │  │  Audio Agent       │ │
│  │ 文本情绪分析     │  │  音频情绪分析      │ │
│  └────────┬─────────┘  └─────────┬──────────┘ │
│           │                      │             │
│           └──────────┬───────────┘             │
│                      │                         │
│           ┌──────────▼──────────┐              │
│           │  Synthesis Agent    │              │
│           │  综合分析与输出     │              │
│           └─────────────────────┘              │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 项目结构

```
emotion_analysor/
├── agents/              # CrewAI Agent 定义
│   ├── emotion_agent.py     # 文本情绪识别Agent
│   ├── audio_agent.py       # 音频分析Agent
│   └── synthesis_agent.py   # 综合分析Agent
├── tasks/               # 任务定义
│   └── emotion_tasks.py     # 情绪识别任务
├── tools/               # 自定义工具
│   ├── audio_processor.py   # 音频处理工具
│   └── emotion_analyzer.py  # 情绪分析工具
├── crew/                # Crew 协作系统
│   └── emotion_crew.py      # EmotionDetectionCrew
├── static/              # 前端文件
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── uploads/             # 音频文件上传目录
├── config.py            # 配置文件
├── models.py            # 数据模型
├── server.py            # FastAPI 服务器
├── requirements.txt     # 依赖列表
├── env_template.txt     # 环境变量模板
└── README.md           # 项目文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果从git获取）
cd emotion_analysor

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env_template.txt` 为 `.env` 并填入你的配置：

```bash
cp env_template.txt .env
```

编辑 `.env` 文件：

```env
# DashScope API 配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here
DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 模型配置
LLM_MODEL=qwen-omni
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 3. 获取 DashScope API Key

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建 API Key
4. 将 API Key 填入 `.env` 文件

### 4. 启动服务

#### 方式一：使用启动脚本（推荐）

```bash
./start.sh
```

启动脚本会自动：
- 检查并安装依赖
- 检查 `.env` 配置
- 生成 HTTPS 证书（如果不存在）
- 启动 HTTPS 服务器

#### 方式二：手动启动

```bash
# 生成 SSL 证书（首次运行）
./generate_cert.sh

# 启动服务器
python server.py
```

服务启动后访问：**https://localhost:8000**

⚠️ **重要提示**：
- 系统默认使用 HTTPS 协议，这是为了支持浏览器录音功能
- 开发环境使用自签名证书，浏览器会显示安全警告，这是正常的
- 点击"高级" > "继续访问"即可
- 详细的 HTTPS 配置说明请参考 [HTTPS_SETUP.md](HTTPS_SETUP.md)

## 📖 使用指南

### 文本情绪识别

1. 在"文本输入"框中输入需要分析的文本
2. 点击"开始分析"按钮
3. 等待AI分析完成
4. 查看识别结果（主要情绪、所有情绪、综合分析）

### 语音情绪识别

1. 点击或拖拽音频文件到"音频上传"区域
2. 支持的格式：MP3, WAV, M4A, OGG, FLAC
3. 文件上传成功后点击"开始分析"
4. 系统会分析语音特征和情感信号

### 结合对话历史

- 系统自动保存对话历史（最近10条）
- 情绪分析会考虑对话上下文
- 可随时点击"清空历史"重置

## 🎯 API 接口

### 健康检查

```bash
GET /health
```

响应示例：
```json
{
  "status": "healthy",
  "timestamp": "2025-10-16T12:00:00",
  "version": "1.0.0"
}
```

### 上传音频

```bash
POST /api/upload_audio
Content-Type: multipart/form-data

file: [音频文件]
```

响应示例：
```json
{
  "success": true,
  "filename": "uuid.mp3",
  "file_path": "/path/to/file",
  "file_size": 1024000
}
```

### 情绪识别

```bash
POST /api/emotion_detect
Content-Type: application/json

{
  "text": "今天真的太开心了！",
  "audio_url": "/uploads/audio.mp3",
  "conversation_history": [
    {"role": "user", "content": "我今天遇到了一件事"},
    {"role": "assistant", "content": "什么事情呢？"}
  ]
}
```

响应示例：
```json
{
  "success": true,
  "emotions": [
    {
      "emotion": "开心",
      "confidence": 0.95,
      "reason": "用户使用了积极的语气词"
    },
    {
      "emotion": "兴奋",
      "confidence": 0.82,
      "reason": "语调高亢，情绪激动"
    }
  ],
  "primary_emotion": "开心",
  "analysis": "用户当前处于非常愉悦的状态...",
  "timestamp": "2025-10-16T12:00:00"
}
```

## 🎨 技术栈

- **AI 模型**: Qwen-Omni (通过 LiteLLM 访问)
- **后端框架**: FastAPI + Uvicorn
- **AI 框架**: CrewAI + LangChain
- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **数据验证**: Pydantic
- **配置管理**: python-dotenv

## 🔧 配置说明

### 情绪分类

系统支持的情绪类型在 `config.py` 中定义：

```python
EMOTION_CATEGORIES = [
    "开心", "快乐", "兴奋", "满足",
    "悲伤", "难过", "失落", "沮丧",
    "愤怒", "生气", "烦躁", "不满",
    "焦虑", "担心", "紧张", "恐惧",
    # ... 更多情绪类型
]
```

### 模型参数

- `LLM_MODEL`: 使用的模型名称（默认: qwen-omni）
- `LLM_TEMPERATURE`: 生成温度（0-1，默认: 0.7）
- `LLM_MAX_TOKENS`: 最大token数（默认: 4096）

### 文件上传限制

- `MAX_FILE_SIZE`: 50MB
- `ALLOWED_AUDIO_EXTENSIONS`: .mp3, .wav, .m4a, .ogg, .flac

## 🐛 故障排除

### 1. API Key 错误

```
错误: DASHSCOPE_API_KEY 未设置
解决: 检查 .env 文件是否存在且包含有效的 API Key
```

### 2. 模块导入错误

```
错误: No module named 'crewai'
解决: 确保已激活虚拟环境并安装所有依赖
pip install -r requirements.txt
```

### 3. 端口被占用

```
错误: Address already in use
解决: 修改 .env 中的 PORT 配置，或停止占用端口的进程
```

### 4. 文件上传失败

```
错误: 文件上传失败
解决: 
- 检查 uploads/ 目录是否存在
- 检查文件大小是否超过限制
- 检查文件格式是否支持
```

## 📝 开发说明

### 添加新的 Agent

1. 在 `agents/` 目录创建新的 Agent 文件
2. 定义 Agent 的角色、目标和背景故事
3. 在 `crew/emotion_crew.py` 中注册新 Agent

### 添加新的工具

1. 在 `tools/` 目录创建新的工具文件
2. 继承 `BaseTool` 类
3. 实现 `_run` 方法
4. 在相应的 Agent 中注册工具

### 自定义情绪类型

编辑 `config.py` 中的 `EMOTION_CATEGORIES` 列表，添加或修改情绪类型。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 作者

情绪识别系统开发团队

## 🙏 致谢

- [CrewAI](https://www.crewai.com/) - Multi-Agent 框架
- [Qwen](https://tongyi.aliyun.com/) - AI 模型支持
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架

---

**注意**: 本系统仅供学习和研究使用，情绪识别结果仅供参考，不能替代专业的心理咨询。

