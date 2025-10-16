# 系统架构文档

## 概述

智能情绪识别系统采用 Multi-Agent 架构，通过多个专业 AI Agent 协作完成情绪识别任务。

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面 (Web UI)                      │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐      │
│  │ 文本输入   │  │ 音频上传    │  │ 对话历史管理     │      │
│  └────────────┘  └─────────────┘  └──────────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼──────────────────────────────────┐
│                    FastAPI 服务器                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │  API 端点                                          │     │
│  │  • GET  /              - 前端页面                  │     │
│  │  • GET  /health        - 健康检查                  │     │
│  │  • POST /api/upload_audio - 音频上传               │     │
│  │  • POST /api/emotion_detect - 情绪识别             │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              EmotionDetectionCrew (协调层)                    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  任务分配与结果整合                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                   │
│  ┌────────────┬───────────┴───────────┬─────────────┐       │
│  │            │                       │             │       │
│  ▼            ▼                       ▼             │       │
│ ┌──────────┐ ┌────────────┐  ┌────────────────┐   │       │
│ │Emotion   │ │Audio       │  │Synthesis       │   │       │
│ │Agent     │ │Agent       │  │Agent           │   │       │
│ │          │ │            │  │                │   │       │
│ │文本情绪  │ │音频情绪    │  │综合分析        │   │       │
│ │识别      │ │分析        │  │与输出          │   │       │
│ └────┬─────┘ └─────┬──────┘  └────────────────┘   │       │
│      │             │                               │       │
│      │  ┌──────────▼──────────┐                    │       │
│      └─►│     工具层           │◄───────────────────┘       │
│         │                     │                            │
│         │ • EmotionAnalyzer   │                            │
│         │ • AudioProcessor    │                            │
│         └──────────┬──────────┘                            │
└────────────────────┼───────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────┐
│                  AI 模型 (Qwen-Omni)                        │
│  • 文本理解   • 语音理解   • 情绪分析   • 语义推理          │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 前端层 (Frontend)

**文件**: `static/index.html`, `static/css/style.css`, `static/js/app.js`

**职责**:
- 提供用户交互界面
- 处理文本输入和音频上传
- 管理对话历史
- 展示情绪识别结果

**技术**:
- HTML5 + CSS3 (紫蓝渐变主题)
- Vanilla JavaScript (无框架)
- Fetch API 进行 HTTP 通信
- LocalStorage 保存对话历史

### 2. API 层 (FastAPI Server)

**文件**: `server.py`

**职责**:
- 提供 RESTful API 端点
- 处理文件上传
- 请求验证和错误处理
- 协调 Crew 执行

**主要端点**:

```python
GET  /                     # 返回前端页面
GET  /health               # 健康检查
POST /api/upload_audio     # 音频文件上传
POST /api/emotion_detect   # 情绪识别（核心功能）
```

### 3. Crew 协调层 (EmotionDetectionCrew)

**文件**: `crew/emotion_crew.py`

**职责**:
- 协调多个 Agent 的工作
- 任务分配与调度
- 结果整合与解析
- 错误处理与回退

**工作流程**:
```python
1. 接收请求 (文本/音频/对话历史)
2. 创建分析任务
   - 如果有文本 → 创建文本分析任务
   - 如果有音频 → 创建音频分析任务
3. 分配任务给对应的 Agent
4. 收集分析结果
5. 创建综合分析任务
6. 返回最终结果
```

### 4. Agent 层 (Multi-Agent System)

#### 4.1 Emotion Agent (文本情绪识别专家)

**文件**: `agents/emotion_agent.py`

**角色**: 情绪识别专家

**职责**:
- 分析文本中的情绪表达
- 识别情绪关键词和语气
- 结合上下文理解情绪变化
- 提供初步的情绪判断

**使用的工具**:
- EmotionAnalyzerTool

#### 4.2 Audio Agent (音频情绪分析专家)

**文件**: `agents/audio_agent.py`

**角色**: 语音情感分析专家

**职责**:
- 处理音频文件
- 分析语音特征（语调、语速、音量等）
- 识别声学层面的情感信号
- 提供音频情绪判断

**使用的工具**:
- AudioProcessorTool

#### 4.3 Synthesis Agent (综合分析师)

**文件**: `agents/synthesis_agent.py`

**角色**: 情绪综合分析师

**职责**:
- 整合文本和音频分析结果
- 考虑对话历史和上下文
- 识别主要情绪和次要情绪
- 生成结构化的分析报告
- 计算置信度并提供理由

### 5. 工具层 (Tools)

#### 5.1 EmotionAnalyzerTool

**文件**: `tools/emotion_analyzer.py`

**功能**:
- 基于关键词的情绪初步识别
- 提供情绪分析的辅助信息
- 支持上下文分析

#### 5.2 AudioProcessorTool

**文件**: `tools/audio_processor.py`

**功能**:
- 读取音频文件
- 提取音频特征
- 准备音频数据供 AI 分析

### 6. 任务层 (Tasks)

**文件**: `tasks/emotion_tasks.py`

**任务类型**:

1. **analyze_text_emotion_task**: 文本情绪分析任务
2. **analyze_audio_emotion_task**: 音频情绪分析任务
3. **synthesize_emotion_task**: 综合分析任务

每个任务包含:
- 详细的任务描述
- 预期的输出格式
- 分配的 Agent
- 上下文信息

### 7. 数据模型层 (Models)

**文件**: `models.py`

**核心模型**:

```python
EmotionDetectRequest    # 请求模型
EmotionDetectResponse   # 响应模型
EmotionResult          # 单个情绪结果
HealthResponse         # 健康检查响应
ErrorResponse          # 错误响应
```

### 8. 配置层 (Configuration)

**文件**: `config.py`

**配置项**:
- API 密钥和端点
- 模型参数（温度、最大token等）
- 服务器配置
- 文件上传限制
- 情绪分类列表

## 数据流

### 完整的情绪识别流程

```
1. 用户输入
   ├─ 文本: "今天真的太开心了！"
   └─ 音频: audio.mp3
   └─ 历史: [...]

2. 前端处理
   ├─ 上传音频文件 → POST /api/upload_audio
   └─ 发送分析请求 → POST /api/emotion_detect

3. 后端接收
   └─ FastAPI 验证请求
       ├─ 检查输入有效性
       └─ 准备 EmotionDetectRequest

4. Crew 协调
   └─ EmotionDetectionCrew.analyze_emotion()
       ├─ 创建文本分析任务
       ├─ 创建音频分析任务
       └─ 创建综合分析任务

5. Agent 执行
   ├─ Emotion Agent → 分析文本
   │   └─ 使用 EmotionAnalyzerTool
   │       └─ 输出: 文本情绪特征
   │
   ├─ Audio Agent → 分析音频
   │   └─ 使用 AudioProcessorTool
   │       └─ 输出: 音频情绪特征
   │
   └─ Synthesis Agent → 综合分析
       └─ 整合所有信息
           └─ 输出: 最终情绪报告

6. 结果处理
   └─ Crew 解析结果
       ├─ 提取情绪列表
       ├─ 确定主要情绪
       ├─ 生成综合分析
       └─ 构建 EmotionDetectResponse

7. 响应返回
   └─ JSON 响应返回前端
       └─ 前端展示结果
```

## 关键技术决策

### 1. 为什么使用 Multi-Agent 架构？

**优势**:
- **专业化**: 每个 Agent 专注于特定领域（文本/音频/综合）
- **可扩展**: 易于添加新的 Agent（如视频分析、生理信号等）
- **可维护**: 职责清晰，便于调试和优化
- **灵活性**: 可以根据输入类型动态选择 Agent

### 2. 为什么使用 CrewAI？

**优势**:
- 内置 Agent 协作机制
- 与 LangChain 良好集成
- 支持多种 LLM 后端
- 提供任务管理和结果聚合

### 3. 为什么选择 Qwen-Omni？

**优势**:
- 多模态支持（文本+音频）
- 中文理解能力强
- API 稳定性好
- 成本效益高

### 4. 前端为什么不使用框架？

**原因**:
- 项目规模适中，Vanilla JS 足够
- 减少依赖和构建复杂度
- 加载速度更快
- 易于理解和定制

## 可扩展性

### 1. 添加新的情绪类型

编辑 `config.py` 中的 `EMOTION_CATEGORIES`:

```python
EMOTION_CATEGORIES = [
    "开心", "悲伤", ...,
    "新情绪类型"  # 添加新情绪
]
```

### 2. 添加新的 Agent

1. 在 `agents/` 创建新的 Agent 文件
2. 定义 Agent 的角色、目标和工具
3. 在 `crew/emotion_crew.py` 中注册
4. 创建对应的 Task

### 3. 添加新的分析维度

例如添加"面部表情分析"：

1. 创建 `agents/facial_agent.py`
2. 创建 `tools/facial_analyzer.py`
3. 在 `EmotionDetectionCrew` 中添加新任务
4. 更新前端支持图片上传

### 4. 支持更多语言

1. 在 `config.py` 添加多语言情绪分类
2. 更新 Agent 的 prompt 支持多语言
3. 前端添加语言切换功能

## 性能优化

### 1. 并行处理

目前文本和音频分析可以并行执行：

```python
# 可以改进为真正的并行
import asyncio
results = await asyncio.gather(
    text_agent.execute(),
    audio_agent.execute()
)
```

### 2. 缓存策略

- 对话历史缓存在客户端 LocalStorage
- 可添加服务端 Redis 缓存常见情绪模式

### 3. 模型优化

- 调整 `LLM_TEMPERATURE` 控制创造性
- 调整 `LLM_MAX_TOKENS` 控制响应长度
- 使用更快的模型处理简单请求

## 安全考虑

### 1. 输入验证

- 文件大小限制（50MB）
- 文件类型白名单
- 文本长度限制

### 2. API 密钥保护

- 使用 `.env` 文件存储
- 不提交到版本控制
- 服务端验证

### 3. 错误处理

- 全局异常处理器
- 友好的错误消息
- 详细的日志记录

## 监控与日志

### 日志级别

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 关键日志点

- API 请求/响应
- Crew 执行开始/结束
- Agent 任务分配
- 错误和异常

## 部署建议

### 开发环境

```bash
python server.py
# 或
./start.sh
```

### 生产环境

```bash
# 使用 Gunicorn + Uvicorn workers
gunicorn server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# 或使用 Docker
docker build -t emotion-analyzer .
docker run -p 8000:8000 emotion-analyzer
```

### 推荐配置

- **CPU**: 2+ 核心
- **内存**: 4GB+
- **存储**: 10GB+（包括上传文件）
- **网络**: 稳定的互联网连接（访问 API）

## 总结

本系统采用现代化的 Multi-Agent 架构，通过专业化分工和协作完成复杂的情绪识别任务。系统设计清晰、易于扩展、性能良好，适合作为情绪分析应用的生产级解决方案。

