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

# 检查可用GPU
check_available_gpu() {
    echo "检查GPU状态..."
    nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits | while IFS=',' read -r gpu_id mem_used mem_total; do
        mem_used=$(echo $mem_used | tr -d ' ')
        mem_total=$(echo $mem_total | tr -d ' ')
        usage_percent=$((mem_used * 100 / mem_total))
        echo "GPU $gpu_id: 使用 ${mem_used}MB / ${mem_total}MB (${usage_percent}%)"
        
        # 如果GPU使用率低于50%，认为可用
        if [ $usage_percent -lt 50 ]; then
            echo "GPU $gpu_id 可用"
            echo $gpu_id > /tmp/available_gpu
            return 0
        fi
    done
    
    # 如果没有找到可用GPU，默认使用GPU 1
    echo "未找到空闲GPU，默认使用GPU 1"
    echo "1" > /tmp/available_gpu
}

SERVER_IP=$(get_server_ip)

echo "=============================================="
echo "🚀 启动 FastAPI 服务器 (智能GPU选择)"
echo "=============================================="
echo "📍 服务器IP: $SERVER_IP"
echo "🌐 服务端口: 30800"
echo "🔗 访问地址: http://$SERVER_IP:30800"
echo "=============================================="

# 检查并选择可用GPU
check_available_gpu
SELECTED_GPU=$(cat /tmp/available_gpu)

echo "🎯 选择使用GPU: $SELECTED_GPU"
export CUDA_VISIBLE_DEVICES=$SELECTED_GPU

# 设置PyTorch CUDA内存配置
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

echo "=============================================="
echo "GPU配置:"
echo "• CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
echo "• PYTORCH_CUDA_ALLOC_CONF=$PYTORCH_CUDA_ALLOC_CONF"
echo "=============================================="

# 启动PDF解析服务
echo "启动PDF解析服务（使用GPU $SELECTED_GPU）..."
marker_server --port 2675 &

# 等待PDF服务启动
echo "等待PDF服务启动..."
sleep 5

# 检查marker服务是否启动成功
if pgrep -f "marker_server" > /dev/null; then
    echo "✅ PDF解析服务启动成功"
else
    echo "❌ PDF解析服务启动失败"
    exit 1
fi

# 启动FastAPI服务
echo "启动FastAPI服务..."
echo "可以通过以下地址访问:"
echo "• 主页: http://$SERVER_IP:30800/"
echo "• API文档: http://$SERVER_IP:30800/docs"
echo "• 报告列表: http://$SERVER_IP:30800/reports"
echo "• 领域上传: http://$SERVER_IP:30800/domain-upload"
echo "=============================================="

uvicorn fastapi_app:app --host 0.0.0.0 --port 30800 --reload
