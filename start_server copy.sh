#!/bin/bash

# 启动PDF解析服务
echo "启动PDF解析服务..."
marker_server --port 2675 &

# 等待PDF服务启动
sleep 2

# 启动FastAPI服务
echo "启动FastAPI服务..."
uvicorn app:app --host 0.0.0.0 --port 8000 --reload