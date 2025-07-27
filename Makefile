# BiliNote 服务管理 Makefile

.PHONY: help start stop restart status clean backend frontend

# 默认目标
help:
	@echo "BiliNote 服务管理命令"
	@echo "======================"
	@echo "make start     - 启动所有服务"
	@echo "make stop      - 停止所有服务"
	@echo "make restart   - 重启所有服务"
	@echo "make status    - 查看服务状态"
	@echo "make backend   - 只启动后端服务"
	@echo "make frontend  - 只启动前端服务"
	@echo "make clean     - 清理PID文件"
	@echo "make help      - 显示此帮助信息"

# 启动所有服务
start:
	@echo "🚀 启动所有服务..."
	@./start.sh

# 停止所有服务
stop:
	@echo "🛑 停止所有服务..."
	@./stop.sh

# 重启所有服务
restart:
	@echo "🔄 重启所有服务..."
	@./restart.sh

# 查看服务状态
status:
	@echo "📊 查看服务状态..."
	@./status.sh

# 只启动后端服务
backend:
	@echo "🔧 启动后端服务..."
	@./start.sh --backend-only

# 只启动前端服务
frontend:
	@echo "🎨 启动前端服务..."
	@./start.sh --frontend-only

# 清理PID文件
clean:
	@echo "🧹 清理PID文件..."
	@rm -f .backend.pid .frontend.pid
	@echo "✅ PID文件已清理"

# 检查依赖
check-deps:
	@echo "🔍 检查依赖..."
	@echo "检查 Python..."
	@python3 --version || (echo "❌ Python 未安装" && exit 1)
	@echo "检查 Node.js..."
	@node --version || (echo "❌ Node.js 未安装" && exit 1)
	@echo "检查 npm..."
	@npm --version || (echo "❌ npm 未安装" && exit 1)
	@echo "✅ 所有依赖检查通过"

# 安装依赖
install-deps:
	@echo "📦 安装依赖..."
	@echo "安装后端依赖..."
	@cd backend && pip install -r requirements.txt
	@echo "安装前端依赖..."
	@cd BillNote_frontend && npm install
	@echo "✅ 依赖安装完成"

# 开发模式启动
dev: check-deps
	@echo "🔧 开发模式启动..."
	@./start.sh

# 生产模式启动（使用Docker）
prod:
	@echo "🚀 生产模式启动..."
	@docker-compose up -d

# 生产模式停止
prod-stop:
	@echo "🛑 生产模式停止..."
	@docker-compose down

# 查看日志
logs:
	@echo "📋 查看服务日志..."
	@if [ -f .backend.pid ]; then echo "后端PID: $$(cat .backend.pid)"; fi
	@if [ -f .frontend.pid ]; then echo "前端PID: $$(cat .frontend.pid)"; fi
	@echo "使用 'ps aux | grep PID' 查看进程详情"

# 快速重启后端
restart-backend:
	@echo "🔄 重启后端服务..."
	@./stop.sh
	@sleep 2
	@./start.sh --backend-only

# 快速重启前端
restart-frontend:
	@echo "🔄 重启前端服务..."
	@./stop.sh
	@sleep 2
	@./start.sh --frontend-only 