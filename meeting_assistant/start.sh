#!/bin/bash

# 会议助手服务启动脚本

echo "╔══════════════════════════════════════════════╗"
echo "║        会议助手服务启动脚本                  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo ""
    echo "⚠️  建议：使用虚拟环境运行"
    echo "   创建虚拟环境: python3 -m venv venv"
    echo "   激活虚拟环境: source venv/bin/activate"
    echo ""
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "❌ 错误: 未找到 .env 文件"
    echo "   请复制 env_template.txt 为 .env 并填入配置"
    echo "   cp env_template.txt .env"
    exit 1
fi

echo "✓ 配置文件已找到"

# 检查依赖
if ! python3 -c "import fastapi" &> /dev/null; then
    echo ""
    echo "⚠️  警告: 依赖包未安装或不完整"
    echo "   正在安装依赖..."
    pip install -r requirements.txt
fi

echo "✓ 依赖检查完成"
echo ""

# 创建uploads目录
mkdir -p uploads

# 启动服务器
echo "🚀 启动服务器..."
echo ""
python3 server.py

