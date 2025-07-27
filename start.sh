#!/bin/bash

# BiliNote 启动脚本
# 用于启动后端和前端服务

echo "🚀 BiliNote 启动脚本"
echo "================================"

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -i:$port >/dev/null 2>&1; then
        echo "⚠️  $service_name (端口: $port) 已在运行"
        return 1
    else
        echo "✅ $service_name (端口: $port) 可用"
        return 0
    fi
}

# 启动后端服务
start_backend() {
    echo ""
    echo "📋 启动后端服务"
    echo "------------------------"
    
    # 检查后端端口
    if ! check_port 8483 "后端服务"; then
        echo "❌ 后端服务端口被占用，请先停止现有服务"
        return 1
    fi
    
    # 检查后端目录是否存在
    if [ ! -d "backend" ]; then
        echo "❌ 错误: backend 目录不存在"
        return 1
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
    
    # 保存后端PID
    echo $BACKEND_PID > .backend.pid
    echo "📁 后端PID已保存到 .backend.pid"
    
    return 0
}

# 启动前端服务
start_frontend() {
    echo ""
    echo "📋 启动前端服务"
    echo "------------------------"
    
    # 检查前端目录是否存在
    if [ ! -d "BillNote_frontend" ]; then
        echo "❌ 错误: BillNote_frontend 目录不存在"
        return 1
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
    
    # 保存前端PID
    echo $FRONTEND_PID > .frontend.pid
    echo "📁 前端PID已保存到 .frontend.pid"
    
    return 0
}

# 检查服务状态
check_services() {
    echo ""
    echo "📋 服务状态检查"
    echo "------------------------"
    
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
}

# 主函数
main() {
    local start_backend_flag=true
    local start_frontend_flag=true
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                start_frontend_flag=false
                shift
                ;;
            --frontend-only)
                start_backend_flag=false
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --backend-only    只启动后端服务"
                echo "  --frontend-only   只启动前端服务"
                echo "  --help, -h        显示帮助信息"
                exit 0
                ;;
            *)
                echo "未知选项: $1"
                echo "使用 --help 查看帮助信息"
                exit 1
                ;;
        esac
    done
    
    # 启动后端服务
    if [ "$start_backend_flag" = true ]; then
        if ! start_backend; then
            echo "❌ 后端服务启动失败"
            exit 1
        fi
    fi
    
    # 启动前端服务
    if [ "$start_frontend_flag" = true ]; then
        if ! start_frontend; then
            echo "❌ 前端服务启动失败"
            exit 1
        fi
    fi
    
    # 检查服务状态
    check_services
    
    echo ""
    echo "🎉 启动完成！"
    echo "================================"
    echo "📝 服务信息:"
    echo "   - 后端服务: http://localhost:8483"
    echo "   - 前端服务: 请查看终端输出获取具体端口"
    echo ""
    echo "💡 提示:"
    echo "   - 使用 './stop.sh' 停止所有服务"
    echo "   - 使用 './restart.sh' 重启所有服务"
    echo "   - 查看日志: 后端和前端服务都在后台运行"
    echo "   - 手动停止: 使用 'pkill -f main.py' 停止后端"
    echo "   - 手动停止: 使用 'pkill -f npm' 停止前端"
    echo ""
    
    # 等待用户输入
    echo "按 Enter 键退出脚本 (服务将继续在后台运行)..."
    read
}

# 运行主函数
main "$@" 