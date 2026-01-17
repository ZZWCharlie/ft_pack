#!/usr/bin/env python3
"""
网络连通性测试脚本
用于诊断本地到远程服务器的网络连接问题
"""

import subprocess
import socket
import sys
import time

def test_ping(host):
    """测试ping连通性"""
    print(f"🏓 测试ping连通性: {host}")
    try:
        result = subprocess.run(['ping', '-c', '4', host], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {host} - ping成功")
            return True
        else:
            print(f"❌ {host} - ping失败")
            print(f"   输出: {result.stdout.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {host} - ping超时")
        return False
    except Exception as e:
        print(f"❌ {host} - ping错误: {e}")
        return False

def test_port(host, port):
    """测试端口连通性"""
    print(f"🔌 测试端口连通性: {host}:{port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ {host}:{port} - 端口可达")
            return True
        else:
            print(f"❌ {host}:{port} - 端口不可达")
            return False
    except Exception as e:
        print(f"❌ {host}:{port} - 测试错误: {e}")
        return False

def test_ssh(host, port=22):
    """测试SSH连接"""
    print(f"🔑 测试SSH连接: {host}:{port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        
        if result == 0:
            # 尝试读取SSH banner
            sock.settimeout(5)
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            if 'SSH' in banner:
                print(f"✅ {host}:{port} - SSH服务可达")
                print(f"   SSH Banner: {banner.strip()}")
                return True
            else:
                print(f"⚠️  {host}:{port} - 端口开放但非SSH服务")
                return False
        else:
            print(f"❌ {host}:{port} - SSH端口不可达")
            sock.close()
            return False
    except Exception as e:
        print(f"❌ {host}:{port} - SSH测试错误: {e}")
        return False

def get_local_network_info():
    """获取本地网络信息"""
    print("🌐 本地网络信息:")
    try:
        # 获取默认路由
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   默认路由: {result.stdout.strip()}")
        
        # 获取本地IP
        result = subprocess.run(['hostname', '-I'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   本地IP: {result.stdout.strip()}")
            
    except Exception as e:
        print(f"❌ 获取网络信息失败: {e}")

def suggest_solutions(ping_ok, ssh_ok, port_ok):
    """根据测试结果提供解决方案"""
    print("\n💡 解决方案建议:")
    
    if not ping_ok:
        print("🚫 网络层不通，可能原因:")
        print("   1. 不在同一网络/子网")
        print("   2. 路由器/防火墙阻止ICMP")
        print("   3. 服务器网络配置问题")
        print("   4. 需要VPN连接")
        
        if ssh_ok:
            print("\n✅ SSH可用，推荐使用SSH隧道:")
            print("   ssh -L 8080:localhost:30800 user@192.168.31.196")
            print("   然后访问: http://localhost:8080")
        else:
            print("\n❌ SSH也不可用，请检查:")
            print("   1. 服务器是否在线")
            print("   2. 网络路由配置")
            print("   3. 是否需要VPN连接")
            print("   4. 防火墙设置")
    
    elif ping_ok and not port_ok:
        print("🔥 网络通但端口不通，可能原因:")
        print("   1. 服务器防火墙阻止30800端口")
        print("   2. FastAPI服务未正确启动")
        print("   3. 服务绑定到错误的接口")

def main():
    if len(sys.argv) != 2:
        print("用法: python3 connectivity_test.py <服务器IP>")
        print("示例: python3 connectivity_test.py 192.168.31.196")
        sys.exit(1)
    
    host = sys.argv[1]
    
    print("=" * 60)
    print(f"🔧 网络连通性测试: {host}")
    print("=" * 60)
    
    get_local_network_info()
    print()
    
    # 测试网络连通性
    ping_ok = test_ping(host)
    print()
    
    # 测试SSH连接
    ssh_ok = test_ssh(host)
    print()
    
    # 测试FastAPI端口
    port_ok = test_port(host, 30800)
    print()
    
    # 提供解决方案
    suggest_solutions(ping_ok, ssh_ok, port_ok)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
