# 系统架构文档

## 📐 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│   (Web Browser, Mobile App, Python Client, cURL, etc.)     │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST API
┌─────────────────────────▼───────────────────────────────────┐
│                     FastAPI 服务器                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  API 路由层 (server.py)                                 │ │
│  │  - /api/transcribe      会议转写                        │ │
│  │  - /api/summary         生成纪要                        │ │
│  │  - /api/qa              问答系统                        │ │
│  │  - /api/process-full    完整流程                        │ │
│  └────────────┬───────────────────────────────────────────┘ │
└───────────────┼─────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────┐
│              CrewAI 协作层 (crew/)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MeetingAssistantCrew                                   │ │
│  │  - transcribe_meeting()   协调转写任务                  │ │
│  │  - generate_summary()     协调纪要生成                  │ │
│  │  - answer_question()      协调问答                      │ │
│  │  - process_full_meeting() 协调完整流程                  │ │
│  └────────────┬───────────────────────────────────────────┘ │
└───────────────┼─────────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────────────────┐
│                   Agent 层 (agents/)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Transcription│  │   Summary    │  │      QA      │      │
│  │    Agent     │  │    Agent     │  │    Agent     │      │
│  │              │  │              │  │              │      │
│  │ 角色: 转写专家│  │ 角色: 纪要专家│  │ 角色: 问答专家│      │
│  │ 目标: 文本转换│  │ 目标: 提取要点│  │ 目标: 回答问题│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────┐
│                     Task 层 (tasks/)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - create_transcription_task()  定义转写任务            │ │
│  │  - create_summary_task()        定义纪要生成任务        │ │
│  │  - create_qa_task()             定义问答任务            │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                      Tool 层 (tools/)                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  TranscriptionTool                                      │  │
│  │  - transcribe_audio()   音频转文本                      │  │
│  │  - transcribe_text()    文本处理                        │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                   外部服务层                                   │
│  ┌──────────────┐         ┌──────────────┐                   │
│  │ OpenAI       │         │ OpenAI       │                   │
│  │ Whisper API  │         │ GPT-4 API    │                   │
│  │ (语音识别)    │         │ (文本生成)    │                   │
│  └──────────────┘         └──────────────┘                   │
└───────────────────────────────────────────────────────────────┘
```

## 🏗️ 组件说明

### 1. FastAPI 服务器层 (`server.py`)

**职责：**
- 提供 RESTful API 接口
- 处理 HTTP 请求和响应
- 文件上传管理
- 错误处理和异常捕获
- CORS 配置

**主要端点：**
- `POST /api/transcribe` - 会议转写
- `POST /api/summary` - 生成会议纪要
- `POST /api/qa` - 会议内容问答
- `POST /api/process-full` - 完整流程处理
- `GET /health` - 健康检查

### 2. CrewAI 协作层 (`crew/meeting_crew.py`)

**职责：**
- 协调多个 Agent 的工作
- 管理任务执行流程
- 整合工具和 Agent
- 处理业务逻辑

**核心类：** `MeetingAssistantCrew`

**方法：**
```python
- transcribe_meeting()      # 转写会议
- generate_summary()        # 生成纪要
- answer_question()         # 回答问题
- process_full_meeting()    # 完整流程
```

### 3. Agent 层 (`agents/`)

#### 3.1 转写 Agent (`transcription_agent.py`)
```python
角色: 会议转写专家
目标: 准确地将会议音频/文本转换为结构化记录
能力:
  - 识别不同说话者
  - 标注时间戳
  - 修正识别错误
  - 格式化文本
```

#### 3.2 纪要 Agent (`summary_agent.py`)
```python
角色: 会议纪要专家
目标: 生成清晰、简洁、结构化的会议纪要
能力:
  - 提取关键信息
  - 识别决策事项
  - 整理行动项
  - 结构化输出
```

#### 3.3 问答 Agent (`qa_agent.py`)
```python
角色: 会议内容问答专家
目标: 准确回答关于会议内容的问题
能力:
  - 理解问题意图
  - 搜索相关内容
  - 提供有依据的答案
  - 引用原文
```

### 4. Task 层 (`tasks/meeting_tasks.py`)

**职责：**
- 定义具体任务的描述
- 设置任务的期望输出
- 配置任务参数

**任务类型：**
```python
- create_transcription_task()   # 转写任务
- create_summary_task()         # 纪要任务
- create_qa_task()              # 问答任务
```

### 5. Tool 层 (`tools/transcription_tool.py`)

**职责：**
- 封装外部服务调用
- 提供工具函数
- 处理具体技术细节

**工具类：** `TranscriptionTool`

**方法：**
```python
- transcribe_audio()   # 调用 Whisper API
- transcribe_text()    # 处理文本内容
```

### 6. 数据模型层 (`models.py`)

**职责：**
- 定义请求和响应数据结构
- 数据验证
- 类型注解

**模型：**
```python
- TranscriptionRequest      # 转写请求
- SummaryRequest           # 纪要请求
- QuestionRequest          # 问答请求
- TranscriptionResponse    # 转写响应
- SummaryResponse          # 纪要响应
- QuestionResponse         # 问答响应
- FullMeetingResponse      # 完整处理响应
- ErrorResponse            # 错误响应
```

### 7. 配置层 (`config.py`)

**职责：**
- 管理环境变量
- 配置参数
- 全局常量

**配置项：**
```python
- OPENAI_API_KEY          # OpenAI API 密钥
- OPENAI_MODEL_NAME       # 使用的模型
- SERVER_HOST             # 服务器地址
- SERVER_PORT             # 服务器端口
- UPLOAD_DIR              # 上传目录
- MAX_FILE_SIZE           # 最大文件大小
- ALLOWED_AUDIO_FORMATS   # 支持的音频格式
```

## 🔄 数据流

### 流程1: 会议转写

```
用户请求
  ↓
[POST /api/transcribe]
  ↓
FastAPI 路由 (接收文件/文本)
  ↓
MeetingAssistantCrew.transcribe_meeting()
  ↓
TranscriptionTool.transcribe_audio() → [Whisper API]
  ↓
create_transcription_task() + TranscriptionAgent
  ↓
Crew.kickoff() → [GPT-4 处理]
  ↓
格式化结果
  ↓
返回 JSON 响应
```

### 流程2: 生成会议纪要

```
用户请求 (提供转写文本)
  ↓
[POST /api/summary]
  ↓
FastAPI 路由
  ↓
MeetingAssistantCrew.generate_summary()
  ↓
create_summary_task() + SummaryAgent
  ↓
Crew.kickoff() → [GPT-4 生成纪要]
  ↓
结构化纪要
  ↓
返回 JSON 响应
```

### 流程3: 会议问答

```
用户请求 (提供会议内容和问题)
  ↓
[POST /api/qa]
  ↓
FastAPI 路由
  ↓
MeetingAssistantCrew.answer_question()
  ↓
create_qa_task() + QAAgent
  ↓
Crew.kickoff() → [GPT-4 生成答案]
  ↓
带引用的答案
  ↓
返回 JSON 响应
```

### 流程4: 完整处理

```
用户请求
  ↓
[POST /api/process-full]
  ↓
MeetingAssistantCrew.process_full_meeting()
  ↓
步骤1: transcribe_meeting()
  ↓
步骤2: generate_summary()
  ↓
组合结果
  ↓
返回完整响应
```

## 🔧 技术栈

### 核心框架
- **CrewAI**: Multi-agent 协作框架
- **FastAPI**: 高性能 Web 框架
- **LangChain**: LLM 应用框架

### AI 服务
- **OpenAI GPT-4**: 文本生成和分析
- **OpenAI Whisper**: 语音转文本

### 支持库
- **Pydantic**: 数据验证
- **Uvicorn**: ASGI 服务器
- **python-dotenv**: 环境变量管理

## 🎯 设计原则

### 1. 单一职责原则
每个组件只负责一个特定功能：
- Agent 负责角色行为
- Task 负责任务定义
- Tool 负责具体操作
- Server 负责 API 接口

### 2. 模块化设计
- 清晰的目录结构
- 独立的功能模块
- 可复用的组件

### 3. 可扩展性
- 易于添加新的 Agent
- 易于添加新的功能
- 易于集成新的工具

### 4. 错误处理
- 完善的异常捕获
- 友好的错误信息
- 日志记录

## 📊 性能考虑

### 1. 异步处理
- FastAPI 原生支持异步
- 可以处理并发请求

### 2. 资源管理
- 临时文件自动清理
- 合理的文件大小限制

### 3. 缓存策略
- 可以添加 Redis 缓存
- 减少重复调用

### 4. 负载均衡
- 支持多实例部署
- 水平扩展能力

## 🔐 安全性

### 1. API 密钥管理
- 环境变量存储
- 不在代码中硬编码

### 2. 文件上传安全
- 文件类型验证
- 大小限制
- 自动清理

### 3. CORS 配置
- 可配置允许的源
- 生产环境限制

### 4. 速率限制
- 可添加 API 调用限制
- 防止滥用

## 🚀 扩展建议

### 1. 添加新的 Agent
```python
# agents/your_new_agent.py
def create_your_agent():
    agent = Agent(
        role="你的角色",
        goal="你的目标",
        backstory="背景故事"
    )
    return agent
```

### 2. 添加新的功能
- 在 `crew/meeting_crew.py` 中添加新方法
- 在 `server.py` 中添加新的 API 端点
- 创建对应的数据模型

### 3. 集成其他服务
- 添加数据库支持（PostgreSQL, MongoDB）
- 集成消息队列（RabbitMQ, Redis）
- 添加搜索引擎（Elasticsearch）

### 4. 增强功能
- 会议录音实时转写
- 多语言支持
- 情感分析
- 关键词提取
- 会议质量评分

## 📈 监控和日志

### 建议添加：
1. **结构化日志**
   - 使用 structlog 或 loguru
   - 记录关键操作

2. **性能监控**
   - API 响应时间
   - 成功率统计
   - 错误率追踪

3. **业务指标**
   - 转写字数统计
   - API 调用量
   - 用户使用情况

## 🎓 学习资源

- [CrewAI 文档](https://docs.crewai.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [OpenAI API 文档](https://platform.openai.com/docs)

## 📝 总结

这是一个基于现代 AI 技术栈的会议助手系统：

✅ **模块化设计** - 清晰的架构，易于维护
✅ **可扩展性** - 容易添加新功能
✅ **高性能** - 异步处理，支持并发
✅ **易用性** - RESTful API，完善文档
✅ **生产就绪** - 错误处理，安全性考虑

适合用于：
- 企业会议记录系统
- 在线会议平台集成
- 个人会议助手工具
- AI 服务演示项目

