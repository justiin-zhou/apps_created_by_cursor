#!/bin/bash

# SSL 自签名证书生成脚本
# 用于开发环境的 HTTPS 支持

echo "=========================================="
echo "  🔒 生成自签名 SSL 证书"
echo "=========================================="
echo ""

# 证书目录
CERT_DIR="./certs"
mkdir -p "$CERT_DIR"

# 证书文件路径
CERT_FILE="$CERT_DIR/cert.pem"
KEY_FILE="$CERT_DIR/key.pem"

# 检查证书是否已存在
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "⚠️  证书文件已存在"
    read -p "是否重新生成？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ 保留现有证书"
        exit 0
    fi
fi

echo "📝 正在生成自签名证书..."
echo ""

# 生成私钥和证书（有效期365天）
openssl req -x509 -newkey rsa:4096 -nodes \
    -out "$CERT_FILE" \
    -keyout "$KEY_FILE" \
    -days 365 \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=Emotion Analysor/OU=Dev/CN=localhost" \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 证书生成成功！"
    echo ""
    echo "证书位置："
    echo "  📄 证书文件: $CERT_FILE"
    echo "  🔑 私钥文件: $KEY_FILE"
    echo ""
    echo "⚠️  注意事项："
    echo "  1. 这是自签名证书，浏览器会显示安全警告，这是正常的"
    echo "  2. 在浏览器中访问时，需要手动信任此证书"
    echo "  3. 生产环境请使用正规 CA 签发的证书"
    echo ""
else
    echo "❌ 证书生成失败"
    exit 1
fi

