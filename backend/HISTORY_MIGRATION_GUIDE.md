# BiliNote 历史记录数据库迁移指南

## 概述

BiliNote 现在支持将生成历史记录存储在 PostgreSQL 数据库中，而不是仅仅依赖浏览器的 localStorage。这提供了更好的数据持久性、跨设备同步能力和更强大的数据管理功能。

## 功能特性

### ✅ 已实现的功能

1. **完整的历史记录存储**
   - 任务基本信息（ID、状态、平台等）
   - 音频/视频元数据（标题、封面、时长等）
   - 转录数据（全文、分段、语言等）
   - 生成的笔记内容（包括多版本支持）
   - 表单配置数据

2. **API 端点**
   - `GET /api/get_all_history` - 获取所有历史记录（支持分页）
   - `GET /api/get_history/{task_id}` - 获取特定任务的详细信息
   - `DELETE /api/delete_history/{task_id}` - 删除历史记录
   - `GET /api/get_history_by_video` - 根据视频ID和平台获取历史记录

3. **数据迁移工具**
   - 从 SQLite 到 PostgreSQL 的数据库迁移
   - 从浏览器 localStorage 导入历史数据

4. **自动记录功能**
   - 新任务会自动保存到数据库
   - 任务状态实时更新
   - 完成后保存完整结果

## 使用指南

### 1. 数据库迁移

如果您是从 SQLite 迁移到 PostgreSQL：

```bash
cd backend
python migrate_to_postgres.py
```

### 2. 导入 localStorage 历史数据

如果您需要从浏览器的 localStorage 导入现有的历史数据：

#### 步骤 1: 导出 localStorage 数据

1. 在浏览器中打开 BiliNote 前端页面
2. 按 F12 打开开发者工具
3. 在控制台执行以下命令：
   ```javascript
   console.log(JSON.stringify(JSON.parse(localStorage.getItem('task-storage'))))
   ```
4. 复制输出的 JSON 数据

#### 步骤 2: 保存导出数据

将复制的 JSON 数据保存到 `backend/localStorage_export.json` 文件中

#### 步骤 3: 执行导入

```bash
cd backend
python import_localStorage_history.py
```

### 3. API 使用示例

#### 获取所有历史记录
```bash
curl http://localhost:8483/api/get_all_history
```

#### 获取特定任务详情
```bash
curl http://localhost:8483/api/get_history/your-task-id
```

#### 删除历史记录
```bash
curl -X DELETE http://localhost:8483/api/delete_history/your-task-id
```

#### 分页获取历史记录
```bash
curl "http://localhost:8483/api/get_all_history?limit=10&offset=0"
```

## 数据库表结构

### history 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | integer | 主键，自增 |
| task_id | varchar | 任务唯一标识符 |
| status | varchar | 任务状态（PENDING、RUNNING、SUCCESS、FAILED） |
| platform | varchar | 平台名称（bilibili、youtube等） |
| title | varchar | 视频标题 |
| cover_url | varchar | 封面图片URL |
| duration | integer | 视频时长（秒） |
| file_path | varchar | 音频文件路径 |
| video_id | varchar | 视频ID |
| raw_info | json | 原始视频信息 |
| transcript_full_text | text | 转录全文 |
| transcript_language | varchar | 转录语言 |
| transcript_raw | json | 原始转录数据 |
| transcript_segments | json | 转录分段数据 |
| markdown_content | text | 生成的笔记内容 |
| markdown_versions | json | 笔记版本历史 |
| form_data | json | 生成时的表单配置 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

## 自动记录流程

当用户生成新笔记时，系统会自动：

1. **任务开始时**：创建历史记录，状态为 "PARSING"
2. **下载完成时**：更新音频元数据信息
3. **转录完成时**：保存转录结果
4. **笔记生成完成时**：保存最终的笔记内容，状态更新为 "SUCCESS"
5. **发生错误时**：状态更新为 "FAILED"

## 兼容性说明

- ✅ 与现有前端 localStorage 存储兼容
- ✅ 支持新旧笔记格式（字符串和版本数组）
- ✅ 向后兼容现有的 video_tasks 表
- ✅ 数据库迁移不会影响现有功能

## 故障排除

### 导入失败

1. 检查 localStorage_export.json 文件格式是否正确
2. 确保数据库连接正常
3. 查看控制台错误信息

### API 调用失败

1. 确认应用程序正在运行（http://localhost:8483）
2. 检查数据库连接配置
3. 查看应用程序日志

### 数据库连接问题

1. 检查 .env 文件中的数据库配置
2. 确认 PostgreSQL 服务正在运行
3. 验证用户权限设置

## 后续开发建议

1. **前端集成**：更新前端代码从 API 读取历史记录而不是 localStorage
2. **搜索功能**：添加按标题、内容搜索的功能
3. **导出功能**：支持导出历史记录为各种格式
4. **同步功能**：实现多设备间的数据同步
5. **备份恢复**：添加数据备份和恢复功能

---

📝 **注意**：目前前端仍使用 localStorage 存储，建议后续更新前端代码以充分利用数据库存储的优势。 