#!/usr/bin/env python3
"""
网络连接诊断脚本
用于排查FastAPI服务无法从外部访问的问题
"""

import socket
import subprocess
import platform
import requests
import time
import sys

def check_port_listening(port=30800):
    """检查端口是否在监听"""
    print(f"🔍 检查端口 {port} 是否在监听...")
    try:
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        if f":{port}" in result.stdout:
            print(f"✅ 端口 {port} 正在监听")
            # 提取监听的具体信息
            lines = result.stdout.split('\n')
            for line in lines:
                if f":{port}" in line and "LISTEN" in line:
                    print(f"   详情: {line.strip()}")
            return True
        else:
            print(f"❌ 端口 {port} 未在监听")
            return False
    except Exception as e:
        print(f"❌ 检查端口时出错: {e}")
        return False

def check_firewall():
    """检查防火墙设置"""
    print("\n🔥 检查防火墙设置...")
    
    # 检查ufw (Ubuntu/Debian)
    try:
        result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("UFW防火墙状态:")
            print(result.stdout)
    except:
        pass
    
    # 检查firewalld (CentOS/RHEL)
    try:
        result = subprocess.run(['firewall-cmd', '--list-ports'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Firewalld开放端口:")
            print(result.stdout)
    except:
        pass
    
    # 检查iptables
    try:
        result = subprocess.run(['iptables', '-L', '-n'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Iptables规则 (简化):")
            lines = result.stdout.split('\n')[:20]  # 只显示前20行
            for line in lines:
                if line.strip():
                    print(f"  {line}")
    except:
        pass

def check_local_access():
    """检查本地访问"""
    print("\n🏠 检查本地访问...")
    urls = [
        "http://127.0.0.1:30800/",
        "http://localhost:30800/"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - 可以访问 (状态码: {response.status_code})")
            else:
                print(f"⚠️  {url} - 响应异常 (状态码: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - 连接被拒绝")
        except requests.exceptions.Timeout:
            print(f"❌ {url} - 连接超时")
        except Exception as e:
            print(f"❌ {url} - 错误: {e}")

def check_network_interfaces():
    """检查网络接口"""
    print("\n🌐 检查网络接口...")
    try:
        if platform.system() == "Linux":
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            current_interface = ""
            
            for line in lines:
                if not line.startswith((' ', '\t')) and ':' in line:
                    current_interface = line.split(':')[1].strip().split('@')[0]
                    print(f"\n接口: {current_interface}")
                elif 'inet ' in line and '127.0.0.1' not in line:
                    ip = line.split()[1].split('/')[0]
                    print(f"  IP: {ip}")
    except Exception as e:
        print(f"❌ 获取网络接口信息失败: {e}")

def check_process():
    """检查FastAPI进程"""
    print("\n🔄 检查FastAPI进程...")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        fastapi_processes = []
        for line in lines:
            if 'fastapi' in line.lower() or 'uvicorn' in line.lower():
                fastapi_processes.append(line)
        
        if fastapi_processes:
            print("找到FastAPI相关进程:")
            for process in fastapi_processes:
                print(f"  {process}")
        else:
            print("❌ 未找到FastAPI相关进程")
            
    except Exception as e:
        print(f"❌ 检查进程时出错: {e}")

def suggest_solutions():
    """提供解决方案建议"""
    print("\n💡 解决方案建议:")
    print("1. 如果端口未监听:")
    print("   - 确保FastAPI服务正在运行")
    print("   - 检查服务是否绑定到0.0.0.0而不是127.0.0.1")
    
    print("\n2. 如果防火墙阻止:")
    print("   - Ubuntu/Debian: sudo ufw allow 30800")
    print("   - CentOS/RHEL: sudo firewall-cmd --add-port=30800/tcp --permanent && sudo firewall-cmd --reload")
    
    print("\n3. 如果网络不通:")
    print("   - 检查路由器/交换机设置")
    print("   - 确认客户端和服务器在同一网络或可路由")
    
    print("\n4. 使用SSH隧道作为临时解决方案:")
    print("   ssh -L 8080:localhost:30800 user@192.168.31.196")
    print("   然后访问: http://localhost:8080")

def main():
    print("=" * 60)
    print("🔧 FastAPI网络连接诊断工具")
    print("=" * 60)
    
    check_process()
    check_port_listening()
    check_firewall()
    check_local_access()
    check_network_interfaces()
    suggest_solutions()
    
    print("\n" + "=" * 60)
    print("诊断完成！请根据上述信息进行相应的修复。")
    print("=" * 60)

if __name__ == "__main__":
    main()
