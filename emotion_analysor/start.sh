#!/bin/bash

# 情绪识别系统启动脚本

echo "=========================================="
echo "  🎭 智能情绪识别系统"
echo "=========================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "📚 检查依赖..."
pip install -q -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "📝 正在从模板创建 .env 文件..."
    cp env_template.txt .env
    echo "✅ 已创建 .env 文件，请编辑并填入你的 API Key"
    echo ""
    echo "按 Ctrl+C 退出，编辑 .env 后重新运行此脚本"
    echo "或按 Enter 继续（如果已配置）"
    read
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p uploads
mkdir -p certs

# 检查并生成 SSL 证书
echo ""
echo "🔒 检查 SSL 证书..."
if [ ! -f "certs/cert.pem" ] || [ ! -f "certs/key.pem" ]; then
    echo "📝 SSL 证书不存在，正在生成..."
    ./generate_cert.sh
else
    echo "✅ SSL 证书已存在"
fi

# 启动服务器
echo ""
echo "=========================================="
echo "  🚀 启动服务器..."
echo "=========================================="
echo ""
echo "访问地址: https://localhost:8000"
echo "📱 如使用自签名证书，浏览器会提示安全警告，请点击'继续访问'"
echo "按 Ctrl+C 停止服务器"
echo ""

python server.py

