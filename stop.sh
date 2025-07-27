#!/bin/bash

# BiliNote 停止脚本
# 用于停止所有后端和前端服务

echo "🛑 BiliNote 停止脚本"
echo "================================"

# 函数：停止进程
stop_process() {
    local port=$1
    local process_name=$2
    
    echo "🛑 正在停止 $process_name (端口: $port)..."
    
    # 查找并杀死占用指定端口的进程
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "   找到进程 PID: $pids"
        kill -9 $pids 2>/dev/null
        echo "   ✅ $process_name 已停止"
    else
        echo "   ℹ️  $process_name 未在运行"
    fi
}

# 函数：停止Python进程
stop_python_process() {
    local script_name=$1
    local process_name=$2
    
    echo "🛑 正在停止 $process_name..."
    
    # 查找并杀死运行指定脚本的Python进程
    local pids=$(ps aux | grep "$script_name" | grep -v grep | awk '{print $2}')
    if [ ! -z "$pids" ]; then
        echo "   找到进程 PID: $pids"
        kill -9 $pids 2>/dev/null
        echo "   ✅ $process_name 已停止"
    else
        echo "   ℹ️  $process_name 未在运行"
    fi
}

# 函数：停止Node.js进程
stop_node_process() {
    local process_name=$1
    
    echo "🛑 正在停止 $process_name..."
    
    # 查找并杀死Node.js进程
    local pids=$(ps aux | grep "node" | grep -v grep | awk '{print $2}')
    if [ ! -z "$pids" ]; then
        echo "   找到进程 PID: $pids"
        kill -9 $pids 2>/dev/null
        echo "   ✅ $process_name 已停止"
    else
        echo "   ℹ️  $process_name 未在运行"
    fi
}

# 停止所有服务
echo "📋 停止所有服务"
echo "------------------------"

# 停止后端服务 (8483端口)
stop_process 8483 "后端服务"

# 停止前端开发服务器 (通常使用3000端口)
stop_process 3000 "前端开发服务器"

# 停止Vite开发服务器 (通常使用5173端口)
stop_process 5173 "Vite开发服务器"

# 停止其他常见的前端端口
stop_process 8080 "前端服务器(8080)"
stop_process 4173 "前端服务器(4173)"

# 停止Python后端进程
stop_python_process "main.py" "Python后端进程"

# 停止Node.js前端进程
stop_node_process "前端Node.js进程"

# 停止npm进程
echo "🛑 正在停止 npm 进程..."
pids=$(ps aux | grep "npm" | grep -v grep | awk '{print $2}')
if [ ! -z "$pids" ]; then
    echo "   找到进程 PID: $pids"
    kill -9 $pids 2>/dev/null
    echo "   ✅ npm 进程已停止"
else
    echo "   ℹ️  npm 进程未在运行"
fi

# 等待进程完全停止
echo "⏳ 等待进程完全停止..."
sleep 2

# 验证端口是否已释放
echo "🔍 验证端口状态..."
ports=(8483 3000 5173 8080 4173)
all_ports_free=true

for port in "${ports[@]}"; do
    if lsof -i:$port >/dev/null 2>&1; then
        echo "   ⚠️  $port端口仍被占用"
        all_ports_free=false
    else
        echo "   ✅ $port端口已释放"
    fi
done

# 清理PID文件
if [ -f ".backend.pid" ]; then
    rm .backend.pid
    echo "📁 已删除 .backend.pid"
fi

if [ -f ".frontend.pid" ]; then
    rm .frontend.pid
    echo "📁 已删除 .frontend.pid"
fi

echo ""
if [ "$all_ports_free" = true ]; then
    echo "🎉 所有服务已成功停止！"
else
    echo "⚠️  部分端口可能仍被占用，请手动检查"
fi

echo "================================" 