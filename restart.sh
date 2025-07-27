#!/bin/bash

# BiliNote 快速重启脚本
# 用于停止现有的后端和前端服务，然后重新启动

echo "🚀 BiliNote 快速重启脚本"
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

# 停止现有服务
echo "📋 步骤 1: 停止现有服务"
echo "------------------------"

# 停止后端服务 (8483端口)
stop_process 8483 "后端服务"

# 停止前端开发服务器 (通常使用3000端口)
stop_process 3000 "前端开发服务器"

# 停止Vite开发服务器 (通常使用5173端口)
stop_process 5173 "Vite开发服务器"

# 停止Python后端进程
stop_python_process "main.py" "Python后端进程"

# 停止Node.js前端进程
stop_node_process "前端Node.js进程"

# 等待进程完全停止
echo "⏳ 等待进程完全停止..."
sleep 2

# 验证端口是否已释放
echo "🔍 验证端口状态..."
if lsof -i:8483 >/dev/null 2>&1; then
    echo "   ⚠️  8483端口仍被占用"
else
    echo "   ✅ 8483端口已释放"
fi

if lsof -i:3000 >/dev/null 2>&1; then
    echo "   ⚠️  3000端口仍被占用"
else
    echo "   ✅ 3000端口已释放"
fi

if lsof -i:5173 >/dev/null 2>&1; then
    echo "   ⚠️  5173端口仍被占用"
else
    echo "   ✅ 5173端口已释放"
fi

echo ""
echo "📋 步骤 2: 启动后端服务"
echo "------------------------"

# 检查后端目录是否存在
if [ ! -d "backend" ]; then
    echo "❌ 错误: backend 目录不存在"
    exit 1
fi

# 进入后端目录并启动服务
cd backend
echo "🔧 启动后端服务..."

# 检查是否有虚拟环境
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo "   使用虚拟环境启动..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
fi

# 启动后端服务
echo "   启动 Python 后端服务 (端口: 8483)..."
python main.py &
BACKEND_PID=$!
echo "   后端服务已启动，PID: $BACKEND_PID"

# 等待后端服务启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查后端服务是否成功启动
if curl -s http://localhost:8483 >/dev/null 2>&1; then
    echo "   ✅ 后端服务启动成功"
else
    echo "   ⚠️  后端服务可能未完全启动，请检查日志"
fi

# 返回项目根目录
cd ..

echo ""
echo "📋 步骤 3: 启动前端服务"
echo "------------------------"

# 检查前端目录是否存在
if [ ! -d "BillNote_frontend" ]; then
    echo "❌ 错误: BillNote_frontend 目录不存在"
    exit 1
fi

# 进入前端目录
cd BillNote_frontend

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 启动前端开发服务器
echo "🔧 启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!
echo "   前端服务已启动，PID: $FRONTEND_PID"

# 等待前端服务启动
echo "⏳ 等待前端服务启动..."
sleep 5

# 返回项目根目录
cd ..

echo ""
echo "📋 步骤 4: 服务状态检查"
echo "------------------------"

# 检查服务状态
echo "🔍 检查服务状态..."

# 检查后端服务
if curl -s http://localhost:8483 >/dev/null 2>&1; then
    echo "   ✅ 后端服务运行正常 (http://localhost:8483)"
else
    echo "   ❌ 后端服务未响应"
fi

# 检查前端服务 (检查常见的开发服务器端口)
FRONTEND_RUNNING=false
for port in 3000 5173 8080 4173; do
    if curl -s http://localhost:$port >/dev/null 2>&1; then
        echo "   ✅ 前端服务运行正常 (http://localhost:$port)"
        FRONTEND_RUNNING=true
        break
    fi
done

if [ "$FRONTEND_RUNNING" = false ]; then
    echo "   ⚠️  前端服务可能未完全启动，请检查终端输出"
fi

echo ""
echo "🎉 重启完成！"
echo "================================"
echo "📝 服务信息:"
echo "   - 后端服务: http://localhost:8483"
echo "   - 前端服务: 请查看终端输出获取具体端口"
echo ""
echo "💡 提示:"
echo "   - 使用 Ctrl+C 停止脚本"
echo "   - 查看日志: 后端和前端服务都在后台运行"
echo "   - 手动停止: 使用 'pkill -f main.py' 停止后端"
echo "   - 手动停止: 使用 'pkill -f npm' 停止前端"
echo ""

# 保存进程ID到文件，方便后续管理
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "📁 进程ID已保存到 .backend.pid 和 .frontend.pid"
echo ""

# 等待用户输入
echo "按 Enter 键退出脚本 (服务将继续在后台运行)..."
read 