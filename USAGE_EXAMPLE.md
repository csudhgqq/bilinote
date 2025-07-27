# BiliNote 服务管理使用示例

## 🚀 快速开始

### 1. 首次使用

```bash
# 查看所有可用命令
make help

# 检查依赖是否安装
make check-deps

# 安装依赖（如果需要）
make install-deps

# 启动所有服务
make start
```

### 2. 日常使用

```bash
# 查看服务状态
make status

# 启动服务
make start

# 停止服务
make stop

# 重启服务
make restart
```

## 📋 详细使用场景

### 场景1：开发调试

```bash
# 1. 启动所有服务
make start

# 2. 查看服务状态
make status

# 3. 修改代码后重启后端
make restart-backend

# 4. 修改前端代码后重启前端
make restart-frontend

# 5. 停止所有服务
make stop
```

### 场景2：只修改后端代码

```bash
# 1. 只启动后端服务
make backend

# 2. 修改后端代码

# 3. 重启后端服务
make restart-backend

# 4. 停止后端服务
make stop
```

### 场景3：只修改前端代码

```bash
# 1. 只启动前端服务
make frontend

# 2. 修改前端代码

# 3. 重启前端服务
make restart-frontend

# 4. 停止前端服务
make stop
```

### 场景4：端口冲突处理

```bash
# 1. 检查端口占用
make status

# 2. 停止所有服务释放端口
make stop

# 3. 重新启动服务
make start
```

### 场景5：依赖问题处理

```bash
# 1. 检查依赖
make check-deps

# 2. 安装缺失的依赖
make install-deps

# 3. 启动服务
make start
```

## 🔧 故障排除示例

### 问题1：后端启动失败

```bash
# 1. 检查状态
make status

# 2. 停止所有服务
make stop

# 3. 检查依赖
make check-deps

# 4. 重新安装后端依赖
cd backend && pip install -r requirements.txt

# 5. 重新启动
make start
```

### 问题2：前端启动失败

```bash
# 1. 检查状态
make status

# 2. 停止所有服务
make stop

# 3. 检查依赖
make check-deps

# 4. 重新安装前端依赖
cd BillNote_frontend && npm install

# 5. 重新启动
make start
```

### 问题3：端口被占用

```bash
# 1. 查看端口占用
lsof -i :8483
lsof -i :5173

# 2. 强制停止占用端口的进程
sudo kill -9 <PID>

# 3. 启动服务
make start
```

## 📊 状态监控示例

### 实时监控服务状态

```bash
# 查看当前状态
make status

# 持续监控（每5秒检查一次）
watch -n 5 make status

# 或者使用循环
while true; do
    clear
    make status
    sleep 5
done
```

### 检查服务响应

```bash
# 检查后端API
curl http://localhost:8483

# 检查前端服务
curl http://localhost:5173

# 检查健康状态
curl http://localhost:8483/health
```

## 🎯 生产环境使用

### 使用Docker Compose

```bash
# 启动生产环境
make prod

# 查看生产环境状态
docker-compose ps

# 查看生产环境日志
docker-compose logs

# 停止生产环境
make prod-stop
```

### 手动管理服务

```bash
# 启动后端
cd backend
python main.py &

# 启动前端
cd BillNote_frontend
npm run dev &

# 停止服务
pkill -f main.py
pkill -f npm
```

## 💡 实用技巧

### 1. 创建别名

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
alias bili-start='cd /path/to/BiliNote && make start'
alias bili-stop='cd /path/to/BiliNote && make stop'
alias bili-status='cd /path/to/BiliNote && make status'
alias bili-restart='cd /path/to/BiliNote && make restart'
```

### 2. 自动启动脚本

创建 `~/.zshrc` 中的自动启动：

```bash
# 进入项目目录时自动检查状态
cd() {
    builtin cd "$@"
    if [[ "$PWD" == */BiliNote ]]; then
        echo "🔍 检查 BiliNote 服务状态..."
        make status
    fi
}
```

### 3. 定时检查

创建定时任务检查服务状态：

```bash
# 添加到 crontab
*/5 * * * * cd /path/to/BiliNote && make status > /dev/null 2>&1
```

## 🚨 注意事项

1. **权限问题**：确保脚本有执行权限
2. **目录位置**：脚本需要在项目根目录运行
3. **依赖检查**：首次使用前检查依赖是否安装
4. **端口冲突**：确保相关端口未被其他程序占用
5. **虚拟环境**：后端服务支持虚拟环境自动检测

## 📞 获取帮助

```bash
# 查看脚本帮助
./start.sh --help

# 查看Makefile帮助
make help

# 查看详细文档
cat SCRIPTS_README.md
``` 