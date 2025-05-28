#!/usr/bin/env python
"""
数据库服务启动脚本

这个脚本用于启动项目所需的所有数据库服务：
- MySQL
- Redis
- Neo4j

使用方法：
    python start_services.py
"""

import os
import sys
import subprocess
import time
import platform
import signal
import atexit

# 服务路径配置
SERVICES = {
    'MySQL': {
        'path': r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe',
        'args': ['--console']
    },
    'Redis': {
        'path': rf'D:\Program Files\Redis\redis-server.exe ',
        'args': [rf'D:\Program Files\Redis\redis.windows.conf']
    },
    'Neo4j': {
        'path': r'D:\Program Files\neo4j-community-4.4.41\bin\neo4j.bat',
        'args': ['console']
    }
}

# 存储所有启动的进程
running_processes = []

def start_services():
    """启动所有数据库服务"""
    print("正在启动数据库服务...")
    
    for service_name, config in SERVICES.items():
        print(f'\n正在启动 {service_name} 服务...')
        try:
            # 检查服务是否已经在运行
            if service_name == 'MySQL':
                result = subprocess.run(['sc', 'query', 'MySQL80'], 
                                     capture_output=True, 
                                     text=True)
                if 'RUNNING' in result.stdout:
                    print(f'{service_name} 服务已经在运行')
                    continue
            elif service_name == 'Redis':
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq redis-server.exe'], 
                                     capture_output=True, 
                                     text=True)
                if 'redis-server.exe' in result.stdout:
                    print(f'{service_name} 服务已经在运行')
                    continue
            elif service_name == 'Neo4j':
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq neo4j.bat'], 
                                     capture_output=True, 
                                     text=True)
                if 'neo4j.bat' in result.stdout:
                    print(f'{service_name} 服务已经在运行')
                    continue
                
            # 启动服务
            process = subprocess.Popen(
                [config['path']] + config['args'],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            running_processes.append((service_name, process))
            print(f'{service_name} 服务启动成功')
            
            # 等待服务完全启动
            time.sleep(5)
            
        except Exception as e:
            print(f'{service_name} 服务启动失败: {e}')
            print('请检查服务路径是否正确，或手动启动服务')
            stop_services()
            sys.exit(1)

def stop_services():
    """停止所有数据库服务"""
    print("\n正在停止数据库服务...")
    
    for service_name, process in reversed(running_processes):
        print(f'正在停止 {service_name} 服务...')
        try:
            if service_name == 'MySQL':
                subprocess.run(['net', 'stop', 'MySQL80'], 
                             check=True, 
                             capture_output=True)
            else:
                process.terminate()
                process.wait(timeout=10)
            print(f'{service_name} 服务已停止')
        except Exception as e:
            print(f'{service_name} 服务停止失败: {e}')
            try:
                process.kill()
            except:
                pass

def signal_handler(signum, frame):
    """处理终止信号"""
    print("\n接收到终止信号，正在停止服务...")
    stop_services()
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 注册退出时的清理函数
    atexit.register(stop_services)
    
    # 启动服务
    start_services()
    
    print("\n所有服务已启动。按 Ctrl+C 停止服务。")
    
    # 保持脚本运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n接收到键盘中断，正在停止服务...")
        stop_services()

if __name__ == '__main__':
    main() 