#!/bin/bash

echo "🔍 检查当前镜像源配置"
echo "=========================="

echo -e "\n📦 Conda镜像源:"
echo "----------------"
conda config --show channels 2>/dev/null || echo "无法获取conda配置"

echo -e "\n🐍 Pip镜像源:"
echo "-------------"
pip config list 2>/dev/null || echo "无法获取pip配置"

echo -e "\n📁 配置文件位置:"
echo "----------------"
echo "Conda配置文件: ~/.condarc"
if [ -f ~/.condarc ]; then
    echo "✅ 存在"
else
    echo "❌ 不存在"
fi

echo "Pip配置文件: ~/.pip/pip.conf"
if [ -f ~/.pip/pip.conf ]; then
    echo "✅ 存在"
else
    echo "❌ 不存在"
fi

echo -e "\n🌐 网络连通性测试:"
echo "-------------------"
echo "测试清华镜像..."
curl -I --connect-timeout 5 https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ 2>/dev/null && echo "✅ 清华conda镜像可达" || echo "❌ 清华conda镜像不可达"
curl -I --connect-timeout 5 https://pypi.tuna.tsinghua.edu.cn/simple/ 2>/dev/null && echo "✅ 清华pip镜像可达" || echo "❌ 清华pip镜像不可达"

echo "测试中科大镜像..."
curl -I --connect-timeout 5 https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ 2>/dev/null && echo "✅ 中科大conda镜像可达" || echo "❌ 中科大conda镜像不可达"
curl -I --connect-timeout 5 https://pypi.mirrors.ustc.edu.cn/simple/ 2>/dev/null && echo "✅ 中科大pip镜像可达" || echo "❌ 中科大pip镜像不可达"

echo "测试阿里云镜像..."
curl -I --connect-timeout 5 https://mirrors.aliyun.com/anaconda/pkgs/main/ 2>/dev/null && echo "✅ 阿里云conda镜像可达" || echo "❌ 阿里云conda镜像不可达"
curl -I --connect-timeout 5 https://mirrors.aliyun.com/pypi/simple/ 2>/dev/null && echo "✅ 阿里云pip镜像可达" || echo "❌ 阿里云pip镜像不可达"

echo -e "\n📋 详细配置内容:"
echo "----------------"
if [ -f ~/.condarc ]; then
    echo "~/.condarc 内容:"
    cat ~/.condarc
else
    echo "~/.condarc 不存在，使用默认配置"
fi

echo ""
if [ -f ~/.pip/pip.conf ]; then
    echo "~/.pip/pip.conf 内容:"
    cat ~/.pip/pip.conf
else
    echo "~/.pip/pip.conf 不存在，使用默认配置"
fi

echo -e "\n✅ 检查完成!"
