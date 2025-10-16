# 🚀 快速启动指南

## 5分钟快速启动

### 第一步：安装依赖

```bash
# 进入项目目录
cd emotion_analysor

# 创建虚拟环境（如果还没有）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 第二步：配置环境变量

```bash
# 复制环境变量模板
cp env_template.txt .env

# 编辑 .env 文件，填入你的 API Key
nano .env  # 或使用其他编辑器
```

在 `.env` 文件中设置：

```env
DASHSCOPE_API_KEY=your_actual_api_key_here
```

**获取 API Key**: 访问 [DashScope 控制台](https://dashscope.console.aliyun.com/)

### 第三步：验证配置

```bash
# 运行配置测试脚本
python test_config.py
```

如果看到 ✅ 全部通过，说明配置正确！

### 第四步：启动服务

**方式一：使用启动脚本（推荐）**

```bash
./start.sh
```

**方式二：直接运行**

```bash
python server.py
```

### 第五步：访问系统

打开浏览器访问：http://localhost:8000

## 快速测试

### 测试1：文本情绪识别

1. 在"文本输入"框中输入：
   ```
   今天真的太开心了！工作进展顺利，还收到了好消息！
   ```

2. 点击"开始分析"

3. 查看识别结果

### 测试2：使用示例脚本

```bash
python example_usage.py
```

这将运行4个预设的情绪识别示例。

## 常见问题

### Q: 提示 "DASHSCOPE_API_KEY 未设置"

**A**: 检查 `.env` 文件是否存在，并确保包含有效的 API Key

### Q: 端口8000被占用

**A**: 修改 `.env` 中的 `PORT` 配置：
```env
PORT=8001
```

### Q: 模块导入错误

**A**: 确保已激活虚拟环境并安装依赖：
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Q: 前端页面打不开

**A**: 
1. 检查服务器是否正常启动
2. 确保 `static/` 目录下的文件完整
3. 查看终端的错误日志

## 下一步

- 📖 阅读 [README.md](README.md) 了解详细功能
- 🏗️ 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解系统架构
- 🔧 根据需要修改 `config.py` 自定义配置
- 🎨 编辑 `static/css/style.css` 自定义界面样式

## 需要帮助？

- 查看日志输出寻找错误信息
- 运行 `python test_config.py` 诊断问题
- 检查 [README.md](README.md) 的故障排除部分

---

**祝使用愉快！** 🎭

