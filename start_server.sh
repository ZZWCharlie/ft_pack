#!/bin/bash

# 获取服务器IP地址
get_server_ip() {
    # 尝试获取主要IP地址
    local ip=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+' | head -1)
    if [ -z "$ip" ]; then
        ip=$(hostname -I | awk '{print $1}')
    fi
    if [ -z "$ip" ]; then
        ip="127.0.0.1"
    fi
    echo "$ip"
}

SERVER_IP=$(get_server_ip)

echo "=============================================="
echo "🚀 启动 FastAPI 服务器"
echo "=============================================="
echo "📍 服务器IP: $SERVER_IP"
echo "🌐 服务端口: 30800"
echo "🔗 访问地址: http://$SERVER_IP:30800"
echo "=============================================="

# 检查GPU状态
echo "检查GPU状态..."
nvidia-smi

# 设置使用GPU 1（避免GPU 0的内存不足问题）
export CUDA_VISIBLE_DEVICES=1

# 启动PDF解析服务
echo "启动PDF解析服务（使用GPU 1）..."
marker_server --port 2675 &

# 等待PDF服务启动
sleep 2

# 启动FastAPI服务
echo "启动FastAPI服务..."
echo "可以通过以下地址访问:"
echo "• 主页: http://$SERVER_IP:30800/"
echo "• API文档: http://$SERVER_IP:30800/docs"
echo "• 报告列表: http://$SERVER_IP:30800/reports"
echo "=============================================="

uvicorn fastapi_app:app --host 0.0.0.0 --port 30800 --reload