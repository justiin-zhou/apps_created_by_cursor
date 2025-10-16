# 会议助手 API 服务

基于 CrewAI 框架的智能会议助手系统，提供会议转写、纪要生成和智能问答功能。

## 🌟 功能特性

### 1. 会议转写
- 支持多种音频格式（MP3, WAV, M4A, OGG, FLAC）
- 使用 OpenAI Whisper API 进行高精度转写
- 支持直接输入文本内容
- 自动格式化和优化转写结果

### 2. 会议纪要生成
- 自动提取会议关键信息
- 生成结构化会议纪要
- 包含：会议概览、讨论要点、决策事项、行动项、下一步计划

### 3. 智能问答
- 基于会议内容回答问题
- 提供引用和上下文
- 准确识别会议中涉及的内容

### 4. 完整流程处理
- 一键完成：转写 → 纪要生成
- 适合快速处理会议记录

## 🏗️ 项目架构

```
meeting_assistant/
├── agents/                 # Agent定义
│   ├── transcription_agent.py  # 转写专家
│   ├── summary_agent.py        # 纪要专家
│   └── qa_agent.py            # 问答专家
├── tasks/                  # 任务定义
│   └── meeting_tasks.py
├── tools/                  # 工具类
│   └── transcription_tool.py
├── crew/                   # CrewAI协作系统
│   └── meeting_crew.py
├── config.py              # 配置文件
├── models.py              # 数据模型
├── server.py              # FastAPI服务器
├── requirements.txt       # 依赖包
└── README.md             # 说明文档
```

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8 或更高版本。

```bash
# 克隆或进入项目目录
cd meeting_assistant

# 创建虚拟环境（推荐）
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

创建 `.env` 文件（参考 `env_template.txt`）：

```bash
# 复制模板
cp env_template.txt .env

# 编辑 .env 文件，填入你的配置
nano .env
```

`.env` 文件内容：

```env
# OpenAI API配置（必需）
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL_NAME=gpt-4

# 服务器配置（可选）
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### 3. 启动服务器

```bash
python server.py
```

服务器启动后，你将看到：

```
╔══════════════════════════════════════════════╗
║        会议助手 API 服务器启动中...          ║
╚══════════════════════════════════════════════╝

🚀 服务地址: http://0.0.0.0:8000
📚 API文档: http://0.0.0.0:8000/docs
📖 ReDoc文档: http://0.0.0.0:8000/redoc
```

## 📖 API 使用指南

### API 文档

访问 `http://localhost:8000/docs` 查看交互式 API 文档（Swagger UI）。

### 主要端点

#### 1. 健康检查

```bash
GET /health
```

#### 2. 转写会议

```bash
POST /api/transcribe
```

**支持两种方式：**

**方式一：上传音频文件**

```bash
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "audio_file=@meeting.mp3" \
  -F "language=zh"
```

**方式二：直接提供文本**

```bash
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "text_content=会议内容文本..." \
  -F "language=zh"
```

**响应示例：**

```json
{
  "raw_transcription": "原始转写文本...",
  "formatted_transcription": "格式化后的转写文本...",
  "status": "success"
}
```

#### 3. 生成会议纪要

```bash
POST /api/summary
```

**请求示例：**

```bash
curl -X POST "http://localhost:8000/api/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "transcription": "会议转写文本..."
  }'
```

**响应示例：**

```json
{
  "summary": "## 会议概览\n...\n## 主要讨论点\n...",
  "status": "success"
}
```

#### 4. 会议问答

```bash
POST /api/qa
```

**请求示例：**

```bash
curl -X POST "http://localhost:8000/api/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_content": "会议内容...",
    "question": "会议中讨论了哪些关键决策？"
  }'
```

**响应示例：**

```json
{
  "question": "会议中讨论了哪些关键决策？",
  "answer": "根据会议内容，主要讨论了以下决策：...",
  "status": "success"
}
```

#### 5. 完整处理（转写 + 纪要）

```bash
POST /api/process-full
```

**请求示例：**

```bash
curl -X POST "http://localhost:8000/api/process-full" \
  -F "audio_file=@meeting.mp3" \
  -F "language=zh"
```

**响应示例：**

```json
{
  "transcription": {
    "raw_transcription": "...",
    "formatted_transcription": "...",
    "status": "success"
  },
  "summary": {
    "summary": "...",
    "status": "success"
  },
  "status": "success"
}
```

## 🧪 Python 客户端示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 1. 转写会议（文本方式）
response = requests.post(
    f"{BASE_URL}/api/transcribe",
    data={
        "text_content": "今天我们讨论了产品路线图...",
        "language": "zh"
    }
)
transcription = response.json()
print(transcription["formatted_transcription"])

# 2. 生成纪要
response = requests.post(
    f"{BASE_URL}/api/summary",
    json={
        "transcription": transcription["formatted_transcription"]
    }
)
summary = response.json()
print(summary["summary"])

# 3. 问答
response = requests.post(
    f"{BASE_URL}/api/qa",
    json={
        "meeting_content": transcription["formatted_transcription"],
        "question": "会议的主要决策是什么？"
    }
)
qa_result = response.json()
print(qa_result["answer"])
```

## 🎯 使用场景

### 1. 会议记录自动化
- 上传会议录音，自动生成转写和纪要
- 节省人工记录时间

### 2. 会议内容回顾
- 基于会议内容快速查找信息
- 回答关于会议的具体问题

### 3. 跨语言支持
- 支持多种语言的会议转写
- 自动识别和处理不同语言

### 4. 团队协作
- 通过 API 集成到现有系统
- 支持批量处理多个会议

## ⚙️ 配置说明

### OpenAI API 配置

本项目使用 OpenAI 的以下服务：
- **Whisper API**：用于音频转文本
- **GPT-4/GPT-3.5**：用于智能分析和生成纪要

确保你的 OpenAI API key 有足够的配额。

### 支持的音频格式

- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- OGG (.ogg)
- FLAC (.flac)

### 文件大小限制

默认最大文件大小：100MB（可在 `config.py` 中修改）

## 🔧 高级配置

### 自定义 Agent 行为

你可以在 `agents/` 目录下修改各个 agent 的角色和行为：

```python
# agents/summary_agent.py
agent = Agent(
    role="会议纪要专家",
    goal="生成清晰、简洁、结构化的会议纪要...",
    backstory="...",
    temperature=0.3  # 调整创造性
)
```

### 修改任务提示词

在 `tasks/meeting_tasks.py` 中自定义任务描述和期望输出。

### 更改 LLM 模型

在 `.env` 文件中设置：

```env
OPENAI_MODEL_NAME=gpt-3.5-turbo  # 更便宜的选项
# 或
OPENAI_MODEL_NAME=gpt-4-turbo-preview  # 更强大的选项
```

## 📝 开发指南

### 添加新功能

1. 在 `agents/` 创建新的 agent
2. 在 `tasks/` 定义相应的 task
3. 在 `crew/meeting_crew.py` 中集成
4. 在 `server.py` 中添加 API 端点

### 测试

```bash
# 启动服务器
python server.py

# 在另一个终端测试 API
curl http://localhost:8000/health
```

## 🐛 常见问题

### 1. OpenAI API 错误

**问题**：`AuthenticationError: Invalid API key`

**解决**：检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确。

### 2. 音频转写失败

**问题**：音频文件上传后转写失败

**解决**：
- 确保音频格式支持
- 检查文件大小是否超限
- 验证音频文件未损坏

### 3. 依赖安装问题

**问题**：某些包安装失败

**解决**：
```bash
# 升级 pip
pip install --upgrade pip

# 单独安装问题包
pip install crewai --no-cache-dir
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

## 🙏 致谢

本项目使用了以下开源项目：
- [CrewAI](https://github.com/joaomdmoura/crewai) - Multi-agent 框架
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [OpenAI](https://openai.com/) - AI 服务提供商
- [LangChain](https://www.langchain.com/) - LLM 应用框架

