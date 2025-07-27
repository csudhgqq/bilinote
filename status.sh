#!/bin/bash

# BiliNote 状态检查脚本
# 用于查看当前服务的运行状态

echo "📊 BiliNote 服务状态检查"
echo "================================"

# 检查端口状态
check_port_status() {
    local port=$1
    local service_name=$2
    
    if lsof -i:$port >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port 2>/dev/null)
        echo "   ✅ $service_name (端口: $port) - 运行中 [PID: $pid]"
        return 0
    else
        echo "   ❌ $service_name (端口: $port) - 未运行"
        return 1
    fi
}

# 检查进程状态
check_process_status() {
    local process_name=$1
    local search_pattern=$2
    
    local pids=$(ps aux | grep "$search_pattern" | grep -v grep | awk '{print $2}')
    if [ ! -z "$pids" ]; then
        echo "   ✅ $process_name - 运行中 [PID: $pids]"
        return 0
    else
        echo "   ❌ $process_name - 未运行"
        return 1
    fi
}

# 检查PID文件
check_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid >/dev/null 2>&1; then
            echo "   ✅ $service_name - PID文件存在且进程运行中 [PID: $pid]"
            return 0
        else
            echo "   ⚠️  $service_name - PID文件存在但进程已停止 [PID: $pid]"
            return 1
        fi
    else
        echo "   ❌ $service_name - PID文件不存在"
        return 1
    fi
}

# 检查服务响应
check_service_response() {
    local url=$1
    local service_name=$2
    
    if curl -s "$url" >/dev/null 2>&1; then
        echo "   ✅ $service_name - 响应正常"
        return 0
    else
        echo "   ❌ $service_name - 无响应"
        return 1
    fi
}

echo "📋 端口状态检查"
echo "------------------------"

# 检查后端端口
backend_running=false
if check_port_status 8483 "后端服务"; then
    backend_running=true
fi

# 检查前端端口
frontend_running=false
for port in 5173 3000 8080 4173; do
    if check_port_status $port "前端服务"; then
        frontend_running=true
        break
    fi
done

echo ""
echo "📋 进程状态检查"
echo "------------------------"

# 检查Python后端进程
check_process_status "Python后端进程" "main.py"

# 检查Node.js前端进程
check_process_status "Node.js前端进程" "node.*dev"

# 检查npm进程
check_process_status "npm进程" "npm.*run"

echo ""
echo "📋 PID文件检查"
echo "------------------------"

# 检查后端PID文件
check_pid_file ".backend.pid" "后端服务"

# 检查前端PID文件
check_pid_file ".frontend.pid" "前端服务"

echo ""
echo "📋 服务响应检查"
echo "------------------------"

# 检查后端服务响应
if [ "$backend_running" = true ]; then
    check_service_response "http://localhost:8483" "后端API服务"
else
    echo "   ❌ 后端API服务 - 端口未运行"
fi

# 检查前端服务响应
if [ "$frontend_running" = true ]; then
    for port in 5173 3000 8080 4173; do
        if check_service_response "http://localhost:$port" "前端Web服务"; then
            break
        fi
    done
else
    echo "   ❌ 前端Web服务 - 端口未运行"
fi

echo ""
echo "📋 系统资源使用"
echo "------------------------"

# 检查内存使用
echo "💾 内存使用情况:"
free_memory=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
total_memory=$(vm_stat | grep "Pages total" | awk '{print $3}' | sed 's/\.//')
if [ ! -z "$free_memory" ] && [ ! -z "$total_memory" ]; then
    free_mb=$((free_memory * 4096 / 1024 / 1024))
    total_mb=$((total_memory * 4096 / 1024 / 1024))
    used_mb=$((total_mb - free_mb))
    echo "   总内存: ${total_mb}MB"
    echo "   已使用: ${used_mb}MB"
    echo "   可用内存: ${free_mb}MB"
else
    echo "   无法获取内存信息"
fi

# 检查磁盘使用
echo ""
echo "💿 磁盘使用情况:"
df -h . | tail -1 | awk '{print "   总空间: " $2 "  已使用: " $3 "  可用: " $4 "  使用率: " $5}'

echo ""
echo "📋 总结"
echo "------------------------"

if [ "$backend_running" = true ] && [ "$frontend_running" = true ]; then
    echo "🎉 所有服务运行正常！"
    echo "   - 后端服务: http://localhost:8483"
    echo "   - 前端服务: 请查看上面的端口信息"
elif [ "$backend_running" = true ]; then
    echo "⚠️  后端服务运行正常，前端服务未运行"
elif [ "$frontend_running" = true ]; then
    echo "⚠️  前端服务运行正常，后端服务未运行"
else
    echo "❌ 所有服务都未运行"
    echo "   建议运行 './start.sh' 启动服务"
fi

echo ""
echo "💡 快速操作:"
echo "   - 启动服务: ./start.sh"
echo "   - 停止服务: ./stop.sh"
echo "   - 重启服务: ./restart.sh"
echo "================================" 