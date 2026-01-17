#!/bin/bash

echo "=============================================="
echo "🔍 GPU状态检查工具"
echo "=============================================="

# 检查nvidia-smi是否可用
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi 未找到，请确保安装了NVIDIA驱动"
    exit 1
fi

echo "📊 GPU详细信息:"
nvidia-smi

echo ""
echo "=============================================="
echo "💾 GPU内存使用情况:"
echo "=============================================="

nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | while IFS=',' read -r gpu_id name mem_used mem_total util; do
    mem_used=$(echo $mem_used | tr -d ' ')
    mem_total=$(echo $mem_total | tr -d ' ')
    util=$(echo $util | tr -d ' ')
    name=$(echo $name | tr -d ' ')
    
    usage_percent=$((mem_used * 100 / mem_total))
    
    echo "GPU $gpu_id ($name):"
    echo "  内存使用: ${mem_used}MB / ${mem_total}MB (${usage_percent}%)"
    echo "  GPU利用率: ${util}%"
    
    if [ $usage_percent -lt 50 ] && [ $util -lt 50 ]; then
        echo "  状态: ✅ 可用"
        echo "  建议: export CUDA_VISIBLE_DEVICES=$gpu_id"
    else
        echo "  状态: ⚠️  繁忙"
    fi
    echo ""
done

echo "=============================================="
echo "🚀 启动建议:"
echo "=============================================="
echo "1. 使用修改后的启动脚本:"
echo "   ./start_server_gpu.sh"
echo ""
echo "2. 或手动指定GPU:"
echo "   export CUDA_VISIBLE_DEVICES=1"
echo "   ./start_server.sh"
echo ""
echo "3. 设置内存优化:"
echo "   export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
echo "=============================================="
