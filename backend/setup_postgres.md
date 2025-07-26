# PostgreSQL 数据库迁移指南

## 1. 安装 PostgreSQL

### macOS (使用 Homebrew)
```bash
brew install postgresql
brew services start postgresql
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### CentOS/RHEL
```bash
sudo yum install postgresql postgresql-server
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## 2. 创建数据库和用户

连接到 PostgreSQL：
```bash
sudo -u postgres psql
```

执行以下 SQL 命令：
```sql
-- 创建用户
CREATE USER bili_user WITH PASSWORD 'bili_password';

-- 创建数据库
CREATE DATABASE bili_note OWNER bili_user;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE bili_note TO bili_user;

-- 退出
\q
```

## 3. 测试连接

```bash
psql -h localhost -p 5432 -U bili_user -d bili_note
```

## 4. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

## 5. 执行数据迁移

```bash
cd backend
python migrate_to_postgres.py
```

## 6. 启动应用

确保 `.env` 文件中的 `DATABASE_URL` 设置正确后：

```bash
python main.py
```

## 故障排除

### 连接被拒绝
检查 PostgreSQL 是否运行：
```bash
sudo systemctl status postgresql
```

### 权限问题
确保用户有正确的权限：
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bili_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bili_user;
```

### 端口冲突
如果端口 5432 被占用，可以修改 `.env` 文件中的端口配置。