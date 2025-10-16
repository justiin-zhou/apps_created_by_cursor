# 部署指南

本文档说明如何部署会议助手API服务到生产环境。

## 📋 部署前检查清单

- [ ] Python 3.8+ 已安装
- [ ] 已获取 OpenAI API Key
- [ ] 已准备好服务器或云平台账号
- [ ] 已配置防火墙规则（开放API端口）
- [ ] 已准备好域名（如需要）

## 🚀 部署方式

### 方式 1: 直接部署到 Linux 服务器

#### 1. 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 安装其他依赖
sudo apt install git curl -y
```

#### 2. 下载代码

```bash
# 克隆或上传代码到服务器
cd /opt
sudo mkdir meeting-assistant
sudo chown $USER:$USER meeting-assistant
cd meeting-assistant

# 上传代码文件...
```

#### 3. 配置环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env_template.txt .env
nano .env  # 编辑配置
```

#### 4. 使用 Systemd 管理服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/meeting-assistant.service
```

内容：

```ini
[Unit]
Description=Meeting Assistant API Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/opt/meeting-assistant
Environment="PATH=/opt/meeting-assistant/venv/bin"
ExecStart=/opt/meeting-assistant/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start meeting-assistant

# 设置开机自启
sudo systemctl enable meeting-assistant

# 查看状态
sudo systemctl status meeting-assistant

# 查看日志
sudo journalctl -u meeting-assistant -f
```

#### 5. 配置 Nginx 反向代理（推荐）

安装 Nginx：

```bash
sudo apt install nginx -y
```

创建配置文件：

```bash
sudo nano /etc/nginx/sites-available/meeting-assistant
```

内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    client_max_body_size 100M;  # 允许上传大文件

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/meeting-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. 配置 HTTPS（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 方式 2: Docker 部署

#### 1. 创建 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "server.py"]
```

#### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  meeting-assistant:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL_NAME=${OPENAI_MODEL_NAME}
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
```

#### 3. 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式 3: 云平台部署

#### AWS EC2

1. 创建 EC2 实例（推荐 t3.medium 或更高）
2. 配置安全组（开放端口 80, 443）
3. 按照"方式 1"的步骤部署
4. 使用 Elastic IP 绑定固定IP

#### Google Cloud Platform

1. 创建 Compute Engine 实例
2. 配置防火墙规则
3. 按照"方式 1"的步骤部署
4. 使用 Cloud Load Balancing（可选）

#### Heroku

创建 `Procfile`：

```
web: python server.py
```

部署：

```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

## 🔒 安全建议

### 1. API 密钥管理

```bash
# 不要在代码中硬编码API密钥
# 使用环境变量或密钥管理服务

# AWS Secrets Manager 示例
aws secretsmanager get-secret-value --secret-id openai-api-key
```

### 2. 添加身份验证

在 `server.py` 中添加：

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()
API_TOKEN = os.getenv("API_TOKEN", "your-secret-token")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

# 在路由中使用
@app.post("/api/transcribe", dependencies=[Depends(verify_token)])
async def transcribe_meeting(...):
    ...
```

### 3. 速率限制

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/transcribe")
@limiter.limit("10/minute")
async def transcribe_meeting(...):
    ...
```

### 4. CORS 配置

```python
# 限制允许的源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # 替换为实际域名
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📊 监控和日志

### 1. 配置日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 健康检查

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
```

### 3. 监控工具

- **Prometheus + Grafana**: 系统监控
- **Sentry**: 错误追踪
- **ELK Stack**: 日志分析

## 🔧 性能优化

### 1. 使用 Gunicorn（生产环境）

```bash
pip install gunicorn
```

启动：

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8000
```

### 2. 启用缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def process_cached_request(content_hash):
    # 缓存处理结果
    ...
```

### 3. 异步任务队列

对于长时间运行的任务，使用 Celery：

```bash
pip install celery redis
```

## 📝 维护

### 备份

```bash
# 备份配置
cp .env .env.backup

# 备份上传文件（如果需要）
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz uploads/
```

### 更新

```bash
# 停止服务
sudo systemctl stop meeting-assistant

# 拉取新代码
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl start meeting-assistant
```

## 🆘 故障排查

### 服务无法启动

```bash
# 检查日志
sudo journalctl -u meeting-assistant -n 50

# 检查端口占用
sudo lsof -i :8000

# 检查Python环境
which python
python --version
```

### API 响应慢

- 检查 OpenAI API 配额
- 增加服务器资源
- 启用缓存
- 使用更快的模型（gpt-3.5-turbo）

### 内存不足

```bash
# 监控内存使用
free -h
top

# 增加 swap（临时方案）
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📞 技术支持

如有部署问题，请：
1. 查看日志文件
2. 检查配置文件
3. 参考 README.md
4. 提交 GitHub Issue

## 🎯 下一步

- [ ] 配置监控告警
- [ ] 设置自动备份
- [ ] 实施灾难恢复计划
- [ ] 性能压力测试
- [ ] 安全审计

