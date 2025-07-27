# BiliNote 服务管理脚本

这个目录包含了用于管理 BiliNote 后端和前端服务的便捷脚本。

## 📁 脚本文件

### 🚀 `start.sh` - 启动脚本
启动后端和前端服务，不会停止现有服务。

**用法：**
```bash
# 启动所有服务
./start.sh

# 只启动后端服务
./start.sh --backend-only

# 只启动前端服务
./start.sh --frontend-only

# 显示帮助信息
./start.sh --help
```

### 🛑 `stop.sh` - 停止脚本
停止所有后端和前端服务，释放相关端口。

**用法：**
```bash
./stop.sh
```

### 🔄 `restart.sh` - 重启脚本
停止现有服务，然后重新启动后端和前端服务。

**用法：**
```bash
./restart.sh
```

### 📊 `status.sh` - 状态检查脚本
查看当前服务的运行状态，包括端口、进程、服务响应等详细信息。

**用法：**
```bash
./status.sh
```

## 🎯 功能特性

### 自动端口管理
- 自动检测和释放 8483 端口（后端）
- 自动检测和释放 3000、5173、8080、4173 端口（前端）
- 验证端口状态，确保服务正常启动

### 进程管理
- 自动查找和停止相关进程
- 保存进程 PID 到文件，方便后续管理
- 支持虚拟环境检测和激活

### 服务状态检查
- 自动检查后端服务是否正常响应
- 自动检测前端服务运行端口
- 提供详细的状态反馈

## 📋 使用流程

### 首次启动
1. 确保已安装 Python 和 Node.js
2. 确保后端依赖已安装（`pip install -r requirements.txt`）
3. 确保前端依赖已安装（`npm install`）
4. 运行启动脚本：
   ```bash
   ./start.sh
   ```

### 日常使用
- **启动服务：** `./start.sh`
- **停止服务：** `./stop.sh`
- **重启服务：** `./restart.sh`
- **查看状态：** `./status.sh`

### 故障排除
如果服务启动失败：

1. **检查端口占用：**
   ```bash
   lsof -i :8483  # 检查后端端口
   lsof -i :5173  # 检查前端端口
   ```

2. **手动停止进程：**
   ```bash
   pkill -f main.py  # 停止后端
   pkill -f npm      # 停止前端
   ```

3. **检查日志：**
   - 后端日志：查看 `backend` 目录下的输出
   - 前端日志：查看 `BillNote_frontend` 目录下的输出

## 🔧 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 | 8483 | Python FastAPI 服务 |
| 前端 | 5173 | Vite 开发服务器（默认） |
| 前端 | 3000 | React 开发服务器（备选） |
| 前端 | 8080 | 其他开发服务器（备选） |
| 前端 | 4173 | Vite 预览服务器（备选） |

## 📝 注意事项

1. **权限要求：** 确保脚本有执行权限（`chmod +x *.sh`）
2. **目录结构：** 脚本需要在项目根目录运行
3. **依赖检查：** 脚本会自动检查必要的目录和依赖
4. **虚拟环境：** 支持 `venv` 和 `.venv` 虚拟环境
5. **后台运行：** 服务在后台运行，脚本退出后服务继续运行

## 🚨 故障排除

### 常见问题

**Q: 端口被占用怎么办？**
A: 运行 `./stop.sh` 停止所有服务，然后重新启动。

**Q: 后端启动失败？**
A: 检查 Python 环境和依赖是否正确安装。

**Q: 前端启动失败？**
A: 检查 Node.js 环境和 `node_modules` 是否正确安装。

**Q: 服务启动但无法访问？**
A: 检查防火墙设置和端口是否被其他程序占用。

### 手动操作

如果需要手动管理服务：

```bash
# 启动后端
cd backend
python main.py

# 启动前端
cd BillNote_frontend
npm run dev

# 停止服务
pkill -f main.py
pkill -f npm
```

## 📞 支持

如果遇到问题，请检查：
1. 系统日志
2. 服务输出日志
3. 端口占用情况
4. 依赖安装状态

## 🎯 快速命令参考

### 使用脚本文件
```bash
# 查看服务状态
./status.sh

# 启动所有服务
./start.sh

# 停止所有服务
./stop.sh

# 重启所有服务
./restart.sh

# 只启动后端
./start.sh --backend-only

# 只启动前端
./start.sh --frontend-only
```

### 使用 Makefile（推荐）
```bash
# 查看所有可用命令
make help

# 启动所有服务
make start

# 停止所有服务
make stop

# 重启所有服务
make restart

# 查看服务状态
make status

# 只启动后端
make backend

# 只启动前端
make frontend

# 清理PID文件
make clean

# 检查依赖
make check-deps

# 安装依赖
make install-deps

# 开发模式启动
make dev

# 生产模式启动（Docker）
make prod

# 生产模式停止
make prod-stop
``` 